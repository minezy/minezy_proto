#!/usr/bin/python
import sys
import json
from py2neo import neo4j, node, rel
import neo4j_conn


def contactList(start, count, request=None):

	query = neo4j.CypherQuery(neo4j_conn.g_graph, 
		"match (n:Contact)-[r]-() with n,count(r) as rc return n.name,n.email,rc order by rc desc "
		"skip "+ str(start) + " limit " + str(count)
		)

	contacts = []
	for record in query.stream():
		contact = { 
			'name':  record[0],
			'email': record[1], 
			'links': record[2] 
			} 
		
		if request is not None:
			contact['href'] = 'http://' + request.host + '/1/contact/'+record[1]+'/'
			
		contacts.append( contact )

	return contacts



if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: " + sys.argv[0] + " <start> <count>"
		exit(1)

	neo4j_conn.connect()

	results = contactList(int(sys.argv[1]), int(sys.argv[2]))

	print "\n"
	print results
	print "\n"
