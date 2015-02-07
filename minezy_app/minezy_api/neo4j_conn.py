import sys
from py2neo import Graph

g_session = None

def connect():
	global g_session
	
	try:
		sys.stdout.write("Connect to Neo4j... ")
		g_session = Graph()
		sys.stdout.write("OK\n")
		return g_session
	
	except:
		print
		print "Error:", sys.exc_info()[1]
		exit(1)
		
	return None

