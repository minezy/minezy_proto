import sys
from py2neo import neo4j

global g_graph

def connect():
	global g_graph

	try:
		print "Connect to Neo4j..."
		g_graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
		print "OK"
	except:
		print "Error:", sys.exc_info()[1]
		exit(1)

