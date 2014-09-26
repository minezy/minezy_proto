import sys
from py2neo import cypher

def connect():
	try:
		sys.stdout.write("Connect to Neo4j... ")
		session = cypher.Session("http://localhost:7474")
		
		tx = session.create_transaction()
		sys.stdout.write("contacts index... ")
		tx.append("CREATE CONSTRAINT ON (c:Contact) ASSERT c.email IS UNIQUE")
		tx.execute()
		sys.stdout.write("email index... ")
		tx.append("CREATE CONSTRAINT ON (e:Email) ASSERT e.id IS UNIQUE")
		tx.commit()
		
		sys.stdout.write("OK\n")
		return session
	except:
		print
		print "Error:", sys.exc_info()[1]
		exit(1)
		
	return None

