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

def run_transaction_for_value(session, cypher):
    tx = session.create_transaction()
    tx.append(cypher)
    results = tx.commit()
    return results[0][0]['value']

def get_total(session):
    cypher = "MATCH (n:`Word`) RETURN count(n) as value"
    return run_transaction_for_value(session, cypher)

def get_num_words_with_count_under(session, count):
    cypher = "MATCH (n:`Word`) WHERE n.count < " + str(count) + " RETURN count(n) as value"
    return run_transaction_for_value(session, cypher)

def get_max_count_for_a_word(session):
    cypher = "MATCH (n:`Word`) RETURN max(n.count) as value"
    return run_transaction_for_value(session, cypher)

if __name__ == '__main__':
    session = neo4j_conn.connect()
    total = get_total(session)
    print str(total) + " - Total"
    max_for_word = get_max_count_for_a_word(session)
    print str(max_for_word) + " - Max count for word"
    print ""
    print str (get_num_words_with_count_under(session, 2)) + " - count = 1"
    print str (get_num_words_with_count_under(session, 10)) + " - count < 10"

    print str (get_num_words_with_count_under(session, 1 * 0.01 * max_for_word)) + " - count <= 1% of max count"
    print str (get_num_words_with_count_under(session, 10 * 0.01 * max_for_word)) + " - count <= 10% of max count"
