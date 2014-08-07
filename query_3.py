import datetime
import operator
import email
import email.utils
from py2neo import neo4j, node, rel

global g_graph;
global g_graph_index;


def show_global_stats():

	# Contacts that send, but no one sends to
	ignore_emails = []
	query = neo4j.CypherQuery(g_graph,
		"MATCH (n:Contact)-[r]->(m:Email) where not (n)<-[:TO|CC]-(:Email) RETURN n, count(r) as c ORDER BY c DESC"
		)
	print "Gathering ignorable Contacts..."
	for record in query.stream():
		n = record[0]
		ignore_emails.append(n['email'])

	# Contacts with most Emails
	query = neo4j.CypherQuery(g_graph,
		"MATCH (n:Contact)-[r]-(m:Email) RETURN n, count(r) as c ORDER BY c DESC LIMIT 10"
		)

	print "Contacts with most Emails:"
	for record in query.stream():
		contact = record[0]
		count = record[1]
		print "\t" + contact['name'] + " (" + contact['email'] + "): " + str(count)
		if contact['email'] in ignore_emails:
			print '\t\tspammer'

	# Most Prolific Sender
	query = neo4j.CypherQuery(g_graph,
		"MATCH (n:Contact)-[r]->(m:Email) RETURN n, count(r) as c ORDER BY c DESC LIMIT 10"
		)

	print "Most Prolific Senders:"
	for record in query.stream():
		contact = record[0]
		count = record[1]
		print "\t" + contact['name'] + " (" + contact['email'] + "): " + str(count)
		if contact['email'] in ignore_emails:
			print '\t\tspammer'

	# Most Prolific Receiver
	query = neo4j.CypherQuery(g_graph,
		"MATCH (n:Contact)<-[r]-(m:Email) RETURN n, count(r) as c ORDER BY c DESC LIMIT 10"
		)

	print "Most Prolific Receivers:"
	for record in query.stream():
		contact = record[0]
		count = record[1]
		print "\t" + contact['name'] + " (" + contact['email'] + "): " + str(count)
		if contact['email'] in ignore_emails:
			print '\t\tspammer'

	# Contacts that most people send TO
	query = neo4j.CypherQuery(g_graph,
		"MATCH (a:Contact), a-->()-[:TO]->(b:Contact) RETURN b,count(distinct a) as ac ORDER BY ac DESC LIMIT 10"
		)
	print "Most Sent To:"
	for record in query.stream():
		contact = record[0]
		count = record[1]
		print "\t" + contact['name'] + " (" + contact['email'] + "): " + str(count)
		if contact['email'] in ignore_emails:
			print '\t\tspammer'

	# Contacts that most people send CC
	query = neo4j.CypherQuery(g_graph,
		"MATCH (a:Contact), a-->()-[:CC]->(b:Contact) RETURN b,count(distinct a) as ac ORDER BY ac DESC LIMIT 10"
		)
	print "Most Copied To:"
	for record in query.stream():
		contact = record[0]
		count = record[1]
		print "\t" + contact['name'] + " (" + contact['email'] + "): " + str(count)
		if contact['email'] in ignore_emails:
			print '\t\tspammer'
			
	return

print "Connect to Neo4j..."
g_graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
g_graph_index = g_graph.get_or_create_index(neo4j.Node, "Nodes")
print "OK"

show_global_stats()

print "All Done"
