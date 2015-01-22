import sys
import json
import time
import email
import email.utils
import itertools
import neo4j_conn
import minezy_app.minezy_api.api_v1.query_common 
from neo4j_loader import neo4jLoader
from message_decorator import MessageDecorator
from datetime import datetime
from py2neo import cypher, node, rel

def clear_db(session):
    sys.stdout.write("Clearing")
    sys.stdout.flush()
    count = 1
    while count != 0:
        tx = session.create_transaction()
        tx.append("MATCH (n) WITH n LIMIT 10000 OPTIONAL MATCH (n)-[r]-() DELETE n,r RETURN count(n) as count")
        results = tx.commit()
        count = results[0][0]['count']
        sys.stdout.write(".")
        sys.stdout.flush()


class TestMessageFactory:
    i=1
    count=1000

    def has_next(self):
        return self.i <= self.count

    def next(self):
        email = None
        if self.has_next(): 
            email = MessageDecorator.from_file('test/test_single.eml')
            email.message.replace_header('Message-ID', "<" + str(self.i) + ">")
            email.message.replace_header('Date', time.ctime(self.i*24*60*60))
            email.word_counts = [('one', 1), ('increasing', self.i)]
            self.i = self.i + 1;
        return email


def load(loader, factory):
    while factory.has_next():
        email = factory.next()
        loader.add(email)

    loader.complete()

def test_words(session):
    tx = session.create_transaction()


if __name__ == '__main__':
    session = neo4j_conn.connect()
    clear_db(session)

    loader = neo4jLoader("100", ['froms', 'froms', 'tos', 'words'], "test_depot", True)
    factory = TestMessageFactory()

    load(loader, factory)



