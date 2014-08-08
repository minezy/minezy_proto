import sys
from py2neo import neo4j

global g_graph
global g_graph_index

def connect():
	global g_graph
	global g_graph_index

	try:
		print "Connect to Neo4j..."
		g_graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
		g_graph_index = g_graph.get_or_create_index(neo4j.Node, "Nodes")
		print "OK"
	except:
		print "Error:", sys.exc_info()[1]
		exit(1)

