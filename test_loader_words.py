import sys
import json
import time
import email
import email.utils
import itertools
import neo4j_conn
from neo4j_loader import neo4jLoader
from message_decorator import MessageDecorator
from datetime import datetime
from py2neo import cypher, node, rel

sys.path.append("./minezy_app")

import minezy_api
#from query_words import query_words
#from minezy_app import minezy_api
from minezy_api.api_v1.query_words import query_words
from minezy_api.api_v1.query_dates import query_dates


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

def default_params():
    query_params = {}
    query_params['start'] = 0
    query_params['end'] = 0

    query_params['year'] = 0
    query_params['month'] = 0
    query_params['day'] = 0

    query_params['keyword'] = ''
    query_params['id'] = ''
    query_params['name'] = ''
    query_params['account'] = '100'
    query_params['from'] = []
    query_params['to'] = []
    query_params['cc'] = []
    query_params['bcc'] = []

    query_params['left'] = []
    if len(query_params['left']) == 0:
        query_params['left'] = []
    query_params['right'] = []
    if len(query_params['right']) == 0:
        query_params['right'] = []
    query_params['observer'] = []

    query_params['rel'] = 'ANY'

    query_qparams['index'] = 0
    query_params['limit'] = 0
    query_params['page'] = 1
    if query_params['page'] < 1:
        query_params['page'] = 1

    count = 'SENT|CC|BCC|TO'.replace('|','+').replace(' ','+')
    query_params['count'] = count.split('+')

    query_params['order'] = 'DESC'

    query_params['word'] = []

    return query_params

def find_word(resp_word, word):
    for r in resp_word:
        if r['word'] == word:
            return r
    return None

def count_word(rec, word):
    return find_word(rec, word)['count']


def test_words():
    resp = query_words(100, default_params())
    rec = resp['word']

    assert count_word(rec, 'one') == 1000
    assert count_word(rec, 'increasing') == 500500

def find_month(resp_word, month):
    for r in resp_word:
        if r['month'] == month:
            return r
    return None

def count_month(rec, month):
    return find_month(rec, month)['count']

def test_words_dates():
    params = default_params();
    params['word'] = ['one']
    params['count'] = ['MONTH']
    params['order'] = 'asc'
    params['limit'] = 12
    resp = query_dates(100, params)
    rec = resp['dates']

    print rec

    # There should be one message per day, so count should equal days in a month.
    assert count_month(rec, 1.0) == 31
    # skip February as it's irregular
    assert count_month(rec, 3.0) == 31
    assert count_month(rec, 4.0) == 30
    assert count_month(rec, 5.0) == 31
    assert count_month(rec, 6.0) == 30
    assert count_month(rec, 7.0) == 31
    assert count_month(rec, 8.0) == 31
    assert count_month(rec, 9.0) == 30
    assert count_month(rec, 10.0) == 31
    assert count_month(rec, 11.0) == 30
    assert count_month(rec, 12.0) == 31

def test_contacts_words():
    params = default_params();
    params['left'] = ['team@minezy.com']
    resp = query_words(100, params)
    rec = resp['word']

    assert count_word(rec, 'one') == 1000
    assert count_word(rec, 'increasing') == 500500

def test_contacts_contacts_words():
    params = default_params();
    params['left'] = ['team@minezy.com']
    params['right'] = ['team@minezy.com']
    params['rel'] = 'any'
    params['count'] = ['MONTH']
    resp = query_words(100, params)
    rec = resp['word']

    assert count_word(rec, 'one') == 1000
    assert count_word(rec, 'increasing') == 500500


if __name__ == '__main__':
    session = neo4j_conn.connect()
    clear_db(session)

    loader = neo4jLoader("100", ['froms', 'froms', 'tos', 'words'], "test_depot", True)
    factory = TestMessageFactory()

    load(loader, factory)

    minezy_api.neo4j_conn.g_session = neo4j_conn.g_session

    test_words()
    test_words_dates()
    test_contacts_words()
    # broken:
    #test_contacts_contacts_words()

