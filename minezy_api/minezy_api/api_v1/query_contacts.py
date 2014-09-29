import time
from minezy_api import neo4j_conn


def query_contacts(params, countResults=False):

    t0 = time.time()

    rels = ''
    if len(params['count']):
        rels = ':' + '|'.join(params['count'])

    bWhere = True
    bManualCount = True
    if len(params['from']):
        query_str = "MATCH (m:Contact)-[:SENT]-(e)-[r"+rels+"]-(n:Contact) WHERE ("
        for i, contact in enumerate(params['from']):
            if i > 0:
                query_str += " OR "
            query_str += "m.email='"+contact+"'"
        query_str += ") "
    elif len(params['to']):
        query_str = "MATCH (n:Contact)-[r"+rels+"]-(e)-["+rels+"]-(m:Contact) WHERE ("
        for i, contact in enumerate(params['to']):
            if i > 0:
                query_str += " OR "
            query_str += "m.email='"+contact+"'"
        query_str += ") "

    elif params['start'] or params['end']:
        bWhere = False
        query_str = "MATCH (n:Contact)-[r"+rels+"]-(e:Email) "
    else:
        bWhere = False
        bManualCount = False
        query_str = "MATCH (n:Contact) "
        if len(params['count']):
            for i,cnt in enumerate(params['count']):
                if i == 0:
                    query_str += "WITH n,"
                else:
                    query_str += "+"
                if cnt == 'SENT':
                    query_str += "n.sent"
                elif cnt == 'TO':
                    query_str += "n.to"
                elif cnt == 'CC':
                    query_str += "n.cc"
                elif cnt == 'BCC':
                    query_str += "n.bcc"
            query_str += " AS count "

    if params['start'] or params['end']:
        if not bWhere:
            query_str += "WHERE "
            bWhere = True
        else:
            query_str += "AND "
        if params['start']:
            query_str += "e.timestamp >= {start} "
        if params['start'] and params['end']:
            query_str += "AND "
        if params['end']:
            query_str += "e.timestamp <= {end} "

    if params['keyword']:
        if not bWhere:
            query_str += "WHERE "
            bWhere = True
        else:
            query_str += "AND "
        query_str += "n.name =~ '(?i).*"+params['keyword']+".*' "

    if bManualCount:
        query_str += "WITH n,count(distinct(e)) AS count "
    query_str += "RETURN n.name,n.email,count ORDER BY count " + params['order'] + ", n.name ASC "

    if params['index'] or params['page'] > 1:
        query_str += "SKIP "+ str(params['index'] + ((params['page']-1)*params['limit'])) + " "
    if params['limit']:
        query_str += "LIMIT {limit}"

    if countResults:
        resp = _query_count(query_str, params)
    else:
        # for debugging
        print query_str

        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()

        contacts = []
        count = -1
        for count,record in enumerate(results[0]):
            contact = {
                'name':  record[0],
                'email': record[1],
                'count': record[2]
                }

            contacts.append(contact)

        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['contact'] = contacts

    t1 = time.time()
    resp['_query_time'] = t1-t0

    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"

    # for debugging
    print count_str

    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()

    resp = {'count': results[0][0][0] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp


