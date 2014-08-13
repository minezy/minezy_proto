#!/usr/bin/python
import sys
import datetime
import time
import operator
import email
import email.utils
import math
from flask import request
from py2neo import neo4j, node, rel
import neo4j_conn


def average(s):
	return sum(s) * 1.0 / len(s)

def stddev(s):
	a = average(s)
	v = map(lambda x: (x-a)**2, s)
	return math.sqrt(average(v))

def contactInfo(fromAddr):

	resp = {}

	query = neo4j.CypherQuery(neo4j_conn.g_graph, 
		"MATCH (n:Contact {email:'" + fromAddr + "'}) "
		"OPTIONAL MATCH (n)-[r:Sent]->() "
		"RETURN n,count(r)"
		)
	results = query.execute()

	if len(results) == 0:
		resp['name'] = 'Unknown Contact'
		return resp
	
	c = results[0][0]
	resp['name'] = c['name']
	
	emailSent = int(results[0][1])
	resp['emailSent'] = emailSent

	actions = {}
	actions['sendTo'] = 'http://' + request.host + '/1/contact/' + fromAddr + '/sentTo'
	actions['sentFrom'] = 'http://' + request.host + '/1/contact/' + fromAddr + '/sentFrom'
	actions['privateTo'] = 'http://' + request.host + '/1/contact/' + fromAddr + '/privateTo'
	actions['privateFrom'] = 'http://' + request.host + '/1/contact/' + fromAddr + '/privateFrom'
	resp['actions'] = actions

	# Collect TimeOfDay Sent
	if emailSent == 0:
		return resp
	
	query = neo4j.CypherQuery(neo4j_conn.g_graph, 
		"MATCH (n:Contact {email:'" + fromAddr + "'})-[:Sent]->(e) "
		"RETURN e ORDER BY e.timestamp desc"
		)

	send_tod = [0] * 24
	send_tz = {}
	for record in query.stream():
		e = record[0]
		tod = email.utils.parsedate_tz(e['date'])
		hour = tod[3]
		hour_adj = tod[3] - ((tod[9] + time.altzone) / 3600)
		if hour_adj >= 24:
			hour_adj -= 24
		elif hour_adj < 0:
			hour_adj += 24
		#print str(tod) + "  hour: " + str(hour) + "   hourAdj: " + str(hour_adj)
		send_tod[hour_adj] += 1
		tz = tod[9] / 3600
		send_tz[tz] = send_tz.get(tz,0) + 1

	sorted_tz = sorted(send_tz, key=send_tz.get, reverse=True)
	if len(sorted_tz) > 0:
		resp['timezone'] = str(sorted_tz[0])
		resp['timezones'] = str(sorted_tz)

	sendTimes = []
	for hour,count in enumerate(send_tod):
		if count > 0:
			bar = '#' * count + ' ' + str(count)
		else:
			bar = '-'
		sendTimes.append( { 'hour': str(hour) + ":00", 'count': count, 'zzz':bar })

	resp['sendTimes'] = sendTimes

	sendPref = []
	avg = average(send_tod)
	std = stddev(send_tod)
	start = -1
	end = 0
	for hour,count in enumerate(send_tod):
		if count > (avg+(std/2)):
			if start == -1:
				start = hour
			end = hour
		elif start != -1:
			sendPref.append( { 'from': str(start) + ":00", 'to': str(end+1) + ":00" })
			start = -1
	if start != -1:
		sendPref.append( { 'from': str(start) + ":00", 'to': str(end+1) + ":00" })

	resp['sendPref'] = sendPref

	# determine speed of replies of toAddr to fromAddr
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (n:Contact {email:'" + fromAddr + "'})<-[:SentBy]-(e:Email)-[:InReplyTo]->(e2)-[:SentBy]->(m:Contact) " 
		"RETURN m,collect(e),collect(e2)"
		)
	replyBehavior = []
	replyDeltasTot = []
	for record in query.stream():
		toAddr = record[0]
		ecReply = record[1]
		ecSend = record[2]
		
		replyDeltasPer = []
		for eSend, eReply in zip(ecSend, ecReply):
			tsSend  = int(eSend["timestamp"])
			tsReply = int(eReply["timestamp"])
			replyDeltasPer.append(tsReply - tsSend)
			replyDeltasTot.append(tsReply - tsSend)
		
		rb = { 
			'href': 'http://' + request.host + '/1/emails/' + fromAddr + '/to/' + toAddr['email'] 
			} 
		if len(replyDeltasPer) > 0:
			if len(replyDeltasPer) > 2:
				replyDeltasPer.remove(min(replyDeltasPer))
				replyDeltasPer.remove(max(replyDeltasPer))
			seconds = int(sum(replyDeltasPer) * 1.0 / len(replyDeltasPer))
			rb['reply_time_avg'] = str(datetime.timedelta(seconds=seconds))					
	
		replyBehavior.append(rb)

	if len(replyDeltasTot) > 0:
		seconds = int(sum(replyDeltasTot) * 1.0 / len(replyDeltasTot))
		replyBehavior.append( { 'to':'all', 'reply_time_avg': str(datetime.timedelta(seconds=seconds)) } )

	resp['reply_behavior'] = replyBehavior
							 
	return resp


def contact_sentTo(fromAddr):
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (n:Contact {email:'" + fromAddr + "'})-[:Sent]->(e)-[r:TO]->(m) "
		"WITH m, count(r) as rc "
		"RETURN m.email,rc ORDER BY rc desc"
		)	
	resp = {}
	resp['contact'] = fromAddr
	resp['href'] = 'http://' + request.host + '/1/contact/' + fromAddr

	sentTo = []
	for record in query.stream():
		sentTo.append( {
			'contact': record[0], 
			'href': 'http://' + request.host + '/1/contact/' + record[0],
			'emails':
				{ 
					'count': record[1],
					'href': 'http://' + request.host + '/1/emails/' + fromAddr + '/to/' + record[0],
				}
			} )
	resp['sentTo'] = sentTo
	return resp


def contact_sentFrom(toAddr):
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (n:Contact)-[:Sent]->(e)-[r:TO]-(m:Contact {email:'" + toAddr + "'}) "
		"WITH n, count(r) as rc "
		"RETURN n.email,rc ORDER BY rc desc"
		)	
	resp = {}
	resp['contact'] = toAddr
	resp['href'] = 'http://' + request.host + '/1/contact/' + toAddr

	sentFrom = []
	for record in query.stream():
		sentFrom.append( {
			'contact': record[0], 
			'href': 'http://' + request.host + '/1/contact/' + record[0],
			'emails':
				{ 
					'count': record[1],
					'href': 'http://' + request.host + '/1/emails/' + record[0] + '/to/' +  toAddr,
				}
			} )
	resp['sentFrom'] = sentFrom
	return resp


def contact_privateTo(fromAddr):
	# Single TO person and who it is:
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (n:Contact {email:'" + fromAddr + "'})-[:Sent]->(e)-[r:TO]->() "
		"WITH e,count(r) as tc where tc=1 "
		"OPTIONAL MATCH (e)-[s:CC]->() "
		"WITH e,tc,count(s) as sc where sc=0 "
		"MATCH (e)-[:TO]->(m:Contact) with m,collect(m) as mc "
		"RETURN m.email,length(mc) ORDER BY length(mc) desc"
		)
	resp = {}
	resp['contact'] = fromAddr
	resp['href'] = 'http://' + request.host + '/1/contact/' + fromAddr

	privateTo = []
	for record in query.stream():
		privateTo.append( {
			'contact': record[0], 
			'count': record[1],
			'href': 'http://' + request.host + '/1/contact/' + record[0]
			} )
	resp['privateTo'] = privateTo
	return resp


def contact_privateFrom(toAddr):
	# Single TO person and who it is:
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (e:Email)-[r:TO|CC]->() WITH e,count(r) as tc WHERE tc=1 "
		"MATCH (m:Contact)-[:Sent]->(e)-->(n:Contact {email:'" + toAddr + "'}) "
		"WITH m,count(m) as mc "
		"RETURN m.email,mc ORDER BY mc desc"
		)
	resp = {}
	resp['contact'] = toAddr
	resp['href'] = 'http://' + request.host + '/1/contact/' + toAddr

	privateFrom = []
	for record in query.stream():
		privateFrom.append( {
			'email': record[0], 
			'count': record[1],
			'href': 'http://' + request.host + '/1/contact/' + record[0]
			} )
	resp['privateFrom'] = privateFrom
	return resp


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: " + sys.argv[0] + " <email>"
		exit(1)

	neo4j_conn.connect()

	info = contactInfo(sys.argv[1])
	print '\t' + sys.argv[1] + ':'
	print '\t\tSent ' + str(info['emailSent']) + ' emails'
	print '\t\tLikely TimeZone: ' + str(info['timezone'])
	print '\t\t\t' + str(info['timezones'])
	print '\t\tTime of day emails sent:'
	for st in info['sendTimes']:
		count = int(st['count'])
		if count > 0:
			bar = '#' * count
			print '\t\t\t' + st['hour'] + '\t' + bar + ' ' + str(count)
		else:
			print '\t\t\t' + st['hour'] + '\t' + '-'
	print '\t\tLikes to send email between:'
	for sp in info['sendPref']:
		print '\t\t\t' + sp['from'] + ' to ' + sp['to']

	print
