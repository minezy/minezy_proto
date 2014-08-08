#!/usr/bin/python
import sys
import datetime
import time
import operator
import email
import email.utils
import math
from py2neo import neo4j, node, rel
import neo4j_conn


def average(s):
	return sum(s) * 1.0 / len(s)

def stddev(s):
	a = average(s)
	v = map(lambda x: (x-a)**2, s)
	return math.sqrt(average(v))

def contactInfo(fromAddr):

	resultInfo = {}

	query = neo4j.CypherQuery(neo4j_conn.g_graph, 
		"MATCH (n:Contact {email:'" + fromAddr + "'})-[:Sent]->() "
		"RETURN count(*)"
		)
	results = query.execute()

	resultInfo['emailSent'] = results[0][0]

	# Sent To single person
	#query = neo4j.CypherQuery(neo4j_conn.g_graph, 
	#	"MATCH (n:Contact {email:'paul@paulquinn.com'})-[:Sent]->(e)-[r:TO]->() "
	#	"WITH e,count(r) as tc "
	#	"OPTIONAL MATCH (e)-[s:CC]->() "
	#	"WITH e,tc,count(s) as sc "
	#	"RETURN e,tc,sc"
	#	)
	#results = query.execute()

	# Single TO person and who it is:
	#query = neo4j.CypherQuery(neo4j_conn.g_graph, 
	#	"MATCH (n:Contact {email:'paul@paulquinn.com'})-[:Sent]->(e)-[r:TO]->() "
	#	"WITH e,count(r) as tc where tc=1 "
	#	"OPTIONAL MATCH (e)-[s:CC]->() "
	#	"WITH e,tc,count(s) as sc where sc=0 "
	#	"MATCH (e)-[:TO]->(m:Contact) with m,collect(m) as mc "
	#	"RETURN m,length(mc) ORDER BY length(mc) desc"
	#	)

	# Collect TimeOfDay Sent
	query = query = neo4j.CypherQuery(neo4j_conn.g_graph, 
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

	resultInfo['timezone'] = str(sorted_tz[0])
	resultInfo['timezones'] = str(sorted_tz)

	sendTimes = []
	for hour,count in enumerate(send_tod):
		if count > 0:
			bar = '#' * count + ' ' + str(count)
		else:
			bar = '-'
		sendTimes.append( { 'hour': str(hour) + ":00", 'count': count, 'zzz':bar })

	resultInfo['sendTimes'] = sendTimes

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

	resultInfo['sendPref'] = sendPref
	return resultInfo


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
