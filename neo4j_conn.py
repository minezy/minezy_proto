import sys
from py2neo import cypher

g_session = None

def connect():
	global g_session
	
	try:
		sys.stdout.write("Connect to Neo4j... ")
		g_session = cypher.Session("http://localhost:7474")
		sys.stdout.write("OK\n")
		return g_session
	except:
		print
		print "Error:", sys.exc_info()[1]
		exit(1)
		
	return None


def create_constraints():
	try:
		tx = g_session.create_transaction()
		
		sys.stdout.write("contacts index... ")
		tx.append("CREATE CONSTRAINT ON (c:Contact) ASSERT c.email IS UNIQUE")
		tx.execute()
		
		sys.stdout.write("email index... ")
		tx.append("CREATE CONSTRAINT ON (e:Email) ASSERT e.id IS UNIQUE")
		tx.execute()
		
		sys.stdout.write("names index... ")
		tx.append("CREATE CONSTRAINT ON (n:Name) ASSERT n.name IS UNIQUE")
		tx.commit()
		
		sys.stdout.write("OK\n")
	except:
		print
		print "Error:", sys.exc_info()[1]
	