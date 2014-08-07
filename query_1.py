import datetime
import operator
from py2neo import neo4j, node, rel

global g_graph;
global g_graph_index;


def timeline_for_contact(fromAddr, toAddr):
	global g_graph

	query = neo4j.CypherQuery(g_graph, 
		"MATCH (n:Contact {email:'" + fromAddr + "'})-->(e)-[r:TO]->(m:Contact {email:'" + toAddr +"'}) "
		"RETURN e "
		"ORDER BY e.timestamp"
		)

	results = query.execute()
	count = len(results)
	if count == 0:
		return

	email_first = results[0][0]
	email_last = results[-1][0]

	date_first = datetime.datetime.utcfromtimestamp(email_first["timestamp"])
	date_last = datetime.datetime.utcfromtimestamp(email_last["timestamp"])
	delta_range = date_last - date_first
	delta_last = abs(date_last - datetime.datetime.now())

	print "Conversation range : " + str(delta_range.days) + " days '" + email_first["date"] + "' to '" + email_last["date"] + "'"
	print "Last Conversation  : " + str(delta_last.days) + " days ago"

	if delta_range.days == 0:
		print "Email Frequency    : " + str(delta_range.seconds / count) + " seconds between emails"
	elif count > delta_range.days:
		print "Email Frequency    : " + str(count / delta_range.days) + " emails per day"
	else:
		print "Email Frequency    : " + str(delta_range.days / count) + " days between emails"

	return delta_range, delta_last


def query_for_private_conversations(toAddr):
	global g_graph

	query = neo4j.CypherQuery(g_graph, 
		"MATCH (n:Email)-[r:TO]->(x:Contact {email:'" + toAddr + "'}) with n,x "
		"MATCH (n-[r:TO]-()) with x,n,count(r) as c where c = 1 "
		"MATCH (p:Contact)-->(n) with x,p,count(*) as pc where x-->()-->p "
		"RETURN p,pc "
		"ORDER BY pc desc"
		)

	ranks = {}
	for record in query.stream():
		node = record[0]
		email_count = record[1]

		name = node["name"]
		if not name:
			name = "no name"
		print node["email"] + "\t\t" + name + " emailed you " + str(email_count) + " time(s)"

		delta_range, delta_last = timeline_for_contact(node["email"], toAddr)
		rank = float(0)
		if delta_range.days > 0:
			#rank = (email_count + delta_range.days) / delta_last.days
			#rank = 1.0 - ((email_count + delta_last.days) / float(delta_range.days))
			#rank = 0.5 * email_count + 0.2 * delta_range.days + 1.0 / delta_last.days
			rank = 0.8 * email_count + 0.2 * delta_range.days * (1.0 / (delta_range.days / float(email_count)))
		ranks[node["email"]] = rank

	sorted_rank = sorted(ranks, key=ranks.get, reverse=True)
	for email in sorted_rank:
		print email + " has rank of " + str(ranks[email])



print "Connect to Neo4j..."
g_graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
g_graph_index = g_graph.get_or_create_index(neo4j.Node, "Nodes")
print "OK"


query_for_private_conversations("paul@paulquinn.com")

print "All Done"
