import sys
import json
import time
import email
import email.utils
import itertools
import neo4j_conn
import Queue
import threading
from datetime import datetime
from py2neo import cypher, node, rel
import numpy as np
import pylab as P

#pip install numpy matplotlib

if __name__ == '__main__':
    session = neo4j_conn.connect()
    tx = session.create_transaction()
    
    cypher = "MATCH (n:`Word`)-[r]-(e) WITH n, sum(r.count) as sum RETURN sum,count(n) ORDER BY sum"
    tx.append(cypher)
    results = tx.execute()

    sums = []
    counts = []
    for record in results[0]:
        if record[0] is not None:
            sums.append(record[0])
            counts.append(record[1])

    P.semilogy(sums, counts)
    P.show()
