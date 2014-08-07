import sys
import datetime
import time
import operator
import email
import email.utils
import math
from py2neo import neo4j, node, rel

global g_graph;
global g_graph_index;

def average(s):
	return sum(s) * 1.0 / len(s)

def stddev(s):
	a = average(s)
	v = map(lambda x: (x-a)**2, s)
	return math.sqrt(average(v))

def tally_conversations(fromAddr):
	global g_graph

	# Total Sent
	query = neo4j.CypherQuery(g_graph, 
		"MATCH (n:Contact {email:'" + fromAddr + "'})-[:Sent]->() "
		"RETURN count(*)"
		)
	results = query.execute()

	print fromAddr + ":"
	print "\tSent " + str(results[0][0]) + " emails "

	# Sent To single person
	#query = neo4j.CypherQuery(g_graph, 
	#	"MATCH (n:Contact {email:'paul@paulquinn.com'})-[:Sent]->(e)-[r:TO]->() "
	#	"WITH e,count(r) as tc "
	#	"OPTIONAL MATCH (e)-[s:CC]->() "
	#	"WITH e,tc,count(s) as sc "
	#	"RETURN e,tc,sc"
	#	)
	#results = query.execute()

	# Single TO person and who it is:
	#query = neo4j.CypherQuery(g_graph, 
	#	"MATCH (n:Contact {email:'paul@paulquinn.com'})-[:Sent]->(e)-[r:TO]->() "
	#	"WITH e,count(r) as tc where tc=1 "
	#	"OPTIONAL MATCH (e)-[s:CC]->() "
	#	"WITH e,tc,count(s) as sc where sc=0 "
	#	"MATCH (e)-[:TO]->(m:Contact) with m,collect(m) as mc "
	#	"RETURN m,length(mc) ORDER BY length(mc) desc"
	#	)

	# Collect TimeOfDay Sent
	query = query = neo4j.CypherQuery(g_graph, 
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
	print "\tLikely TimeZone: " + str(sorted_tz[0])
	print "\t\t" + str(send_tz)

	print "\tSends at hours:"
	for hour,count in enumerate(send_tod):
		if count > 0:
			bar = '#' * count
			print "\t\t" + str(hour) + ":00 \t" + bar + " " + str(count)
		else:
			print "\t\t" + str(hour) + ":00 \t-"

	avg = average(send_tod)
	std = stddev(send_tod)
	print "\tavg:" + str(avg)
	print "\tstd:" + str(std)
	start = -1
	end = 0
	print "\tLikes to send email between:"
	for hour,count in enumerate(send_tod):
		if count > (avg+(std/2)):
			if start == -1:
				start = hour
			end = hour
		elif start != -1:
			print "\t\t" + str(start) + ":00 to " + str(end+1) + ":00"
			start = -1
	if start != -1:
		print "\t\t" + str(start) + ":00 to " + str(end+1) + ":00"

	return


print "Connect to Neo4j..."
g_graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
g_graph_index = g_graph.get_or_create_index(neo4j.Node, "Nodes")
print "OK"

if len(sys.argv) == 1:
	print "\tGive email address as argument"
else:
	fromAddr = sys.argv[1]
	tally_conversations(fromAddr)

print "All Done"
