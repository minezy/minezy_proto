#!/usr/bin/python
import sys
import datetime
import time
import operator
import email
import email.utils
import math
from collections import OrderedDict
from py2neo import neo4j, node, rel
import neo4j_conn


def email_list(fromAddr, toAddr, request=None):
	resp = {}
	if request is not None:
		resp['from'] = { 'contact': fromAddr, 'href': 'http://' + request.host + '/1/contact/' + fromAddr }
		resp['to']   = { 'contact': toAddr,   'href': 'http://' + request.host + '/1/contact/' + toAddr }
	else:
		resp['from'] = { 'contact': fromAddr }
		resp['to']   = { 'contact': toAddr }
		
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (:Contact {email:'" + fromAddr + "'})-[:Sent]->(e)-[:TO]->(:Contact {email:'" + toAddr +"'}) "
		"WHERE NOT (e)-[:InReplyTo]->() "
		"RETURN e ORDER BY e.timestamp desc"
		)
	results = query.execute()

	count = len(results)
	if count > 0:
		email_first = results[-1][0]
		email_last = results[0][0]
		date_first = datetime.datetime.utcfromtimestamp(email_first["timestamp"])
		date_last = datetime.datetime.utcfromtimestamp(email_last["timestamp"])
		delta_range = date_last - date_first
		delta_last = abs(date_last - datetime.datetime.now())
	
		if delta_range.days == 0:
			freq = str(delta_range.seconds / count) + " seconds between emails"
		elif count > delta_range.days:
			freq = str(count / delta_range.days) + " emails per day"
		else:
			freq = str(delta_range.days / count) + " days between emails"
	
		resp['conversation_stats'] = {
									'duration': str(delta_range.days) + ' days',
									'first': email_first["date"],
									'last': email_last["date"],
									'frequency': freq,
									'seen': str(delta_last.days) + ' days ago'
									}

	emailInit = []
	for record in results:
		e = record[0]
		if request is not None:
			emailInit.append( {
				'subject': e['subject'], 
				'date': e['date'], 
				'href': 'http://' + request.host + '/1/email/' + e['id'],
				} )
		else:
			emailInit.append( {
				'subject': e['subject'], 
				'date': e['date']
				} )
	resp['emailsInitiated'] = emailInit

	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (:Contact {email:'" + fromAddr + "'})-[:Sent]->(e)-[:TO]->(:Contact {email:'" + toAddr +"'}) "
		"WHERE (e)-[:InReplyTo]->() "
		"RETURN e ORDER BY e.timestamp desc"
		)
	emailReplied = []
	for record in query.stream():
		e = record[0]
		if request is not None:
			emailReplied.append( {
				'subject': e['subject'], 
				'date': e['date'], 
				'href': 'http://' + request.host + '/1/email/' + e['id'],
				} )
		else:
			emailReplied.append( {
				'subject': e['subject'], 
				'date': e['date']
				} )
	resp['emailsReplied'] = emailReplied
	
	# determine speed of replies of toAddr to fromAddr
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (n:Contact {email:'" + toAddr + "'})<-[:SentBy]-(e:Email)-[:InReplyTo]->(e2)-[:SentBy]->(m:Contact {email:'" + fromAddr + "'}) " 
		"RETURN e,e2"
		)
	replyDeltas = []
	for record in query.stream():
		eReply = record[0]
		eSend = record[1]
		tsSend  = int(eSend["timestamp"])
		tsReply = int(eReply["timestamp"])
		replyDeltas.append(tsReply - tsSend)
		
	rb = {}
	if request is not None:
		rb['from'] = 'http://' + request.host + '/1/contact/' + toAddr
		rb['to'] = 'http://' + request.host + '/1/contact/' + fromAddr 
	if len(emailInit) > 0:
		rb['reply_percentage'] = len(emailReplied) * 100.0 / len(emailInit)		
	if len(replyDeltas) > 0:
		if len(replyDeltas) > 2:
			replyDeltas.remove(min(replyDeltas))
			replyDeltas.remove(max(replyDeltas))
		seconds = int(sum(replyDeltas) * 1.0 / len(replyDeltas))
		rb['reply_time_avg'] = str(datetime.timedelta(seconds=seconds))					

	resp['reply_behavior'] = rb
	
	return resp


def email_thread(emailId, request=None):
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (e:Email {id:'" + emailId + "'}) "
		"OPTIONAL MATCH (e)-[:Reply]->(er) "
		"WITH e,er ORDER BY er.timestamp asc "
		"MATCH e-[:SentBy]->(sender) "
		"OPTIONAL MATCH e-[:TO]->(to) "
		"OPTIONAL MATCH e-[:CC]->(cc) "
		"OPTIONAL MATCH e-[:InReplyTo]->(inreplyto) "
		"RETURN e, collect(er), sender, collect(distinct to), collect(distinct cc), inreplyto"
		)
	results = query.execute()

	resp = {}
	eReplies = []
	for record in results:
		e = record[0]
		eRefs = record[1]
		s = record[2]
		to = record[3]
		cc = record[4]
		eRep = record[5]

		resp = {
			'subject': e['subject'], 
			'date': e['date'],
			'id': e['id']
			}
		if request is not None:
			resp['from'] = 'http://' + request.host + '/1/contact/' + s['email']

		if eRep is not None:
			resp['inreplyto'] = eRep['id']
					
		toList = []
		for t in to:
			if request is not None:
				toList.append('http://' + request.host + '/1/contact/' + t['email'])
		
		ccList = []
		for c in cc:
			if request is not None:
				ccList.append('http://' + request.host + '/1/contact/' + c['email'])
		if len(ccList) > 0:
			toList.append( {'cc': ccList } )
		
		resp['to'] = toList
		
#		for er in eRefs:
#			eThread = email_thread(er['id'])
#			if len(eThread) > 0:
#				eReplies.append(eThread)
				
	if len(eReplies) > 0:
		resp['replies'] = eReplies
			
	return resp
				
# 		"MATCH e-[:SentBy]->(sender) "
#		"OPTIONAL MATCH e-[:TO]->(to) "
#		"OPTIONAL MATCH e-[:CC]->(cc) "
	
def email_info(emailId, request=None):
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (e:Email {id:'" + emailId + "'}) "
		"OPTIONAL MATCH (e)-[:Refs|Reply]-(er) "
		"WITH e,er ORDER BY er.timestamp asc "
		"MATCH e-[:SentBy]->(sender) "
		"OPTIONAL MATCH e-[:TO]->(to) "
		"OPTIONAL MATCH e-[:CC]->(cc) "
		"RETURN e, collect(er), sender, collect(distinct to), collect(distinct cc)"
		)
	results = query.execute()

	resp = {}
	eReplies = []
	for record in results:
		e = record[0]
		eRefs = record[1]
		s = record[2]
		to = record[3]
		cc = record[4]

		resp = {
			'subject': e['subject'], 
			'date': e['date'],
			'id': e['id']
			}
		if request is not None:
			resp['from'] = 'http://' + request.host + '/1/contact/' + s['email']

		toList = []
		for t in to:
			if request is not None:
				toList.append('http://' + request.host + '/1/contact/' + t['email'])
		resp['to'] = toList
		
		ccList = []
		for c in cc:
			if request is not None and c['email'] is not None:
				ccList.append('http://' + request.host + '/1/contact/' + c['email'])
		resp['cc'] = ccList
		
		for er in eRefs:
			eThread = email_thread(er['id'])
			if len(eThread) > 0:
				if eThread not in eReplies:
					eReplies.append(eThread)
				
	if len(eReplies) > 0:
		resp['replies'] = eReplies
			
	return resp


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: " + sys.argv[0] + " <emailFrom> <emailTo>"
		exit(1)

	neo4j_conn.connect()

	emails = email_list(sys.argv[1], sys.argv[2])
	print str(emails)
	print

