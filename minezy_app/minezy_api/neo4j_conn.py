import sys
from py2neo import Graph
from py2neo.packages.httpstream import http

g_session = None

def connect():
	global g_session
	
	http.socket_timeout = 9999
	
	try:
		sys.stdout.write("Connect to Neo4j... ")
		g_session = Graph("http://neo4j:admin@localhost:7474/db/data")
		sys.stdout.write("OK\n")
		return g_session
	
	except:
		print
		print "Error:", sys.exc_info()[1]
		exit(1)
		
	return None

