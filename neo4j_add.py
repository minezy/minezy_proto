import sys
import json
import time
import email
import email.utils
import itertools
import neo4j_conn
from py2neo import cypher, node, rel
from numpy.polynomial.polyutils import RankWarning

global g_names
global g_session

def init():
    global g_names
    global g_session
    
    g_session = neo4j_conn.connect()
    
    g_names = {}
    return

def batch_start():
    global g_session
    
    tx = g_session.create_transaction()
    return tx

def batch_commit(tx):
    t0 = time.time()
    sys.stdout.write("Writing batch... ")
    
    tx.commit()
    
    t1 = time.time()
    sys.stdout.write(str(t1-t0) + " seconds\n")
    
    _add_names_to_db()
    return

def add_to_db(email_msg, batch):
    try:
        msgSubject = _get_decoded(email_msg['Subject'])
        msgDate = _get_decoded(email_msg['Date'])
        msgID = _get_decoded(email_msg['Message-ID'])
        msgIDParent = _get_decoded(email_msg['In-Reply-To'])
        date = email.utils.parsedate_tz(msgDate)
        timestamp = email.utils.mktime_tz(date)
        
        if len(msgID) == 0:
            print "Email with no msgID skipped"
            return
        if msgID == "None":
            print "Email with msgID=None skipped"
            return
        
        msgID = msgID.strip("<>")
        msgIDParent = msgIDParent.strip("<>")
        
        # Add From actor
        msgFrom = email.utils.getaddresses(email_msg.get_all('From', ['']))
        msgXFrom = email_msg.get_all('X-From', [''])
        _collect_names(msgFrom[0], msgXFrom[0])
    
        msgEmail = str.lower(msgFrom[0][1])
        props = {"props" : { "id":msgID, "parentId":msgIDParent, "email":msgEmail, "subject":msgSubject, "date":msgDate, "timestamp":timestamp} }
               
        # Add Email
        cypher = "MERGE (e:Email {id:{props}.id}) "
        cypher += "SET e.subject={props}.subject, e.date={props}.date, e.timestamp={props}.timestamp "
        # Add From Actor
        cypher += "MERGE (a:Actor {email:{props}.email}) "
        cypher += "CREATE UNIQUE (a)-[:Sent]->(e), (e)-[:SentBy]->(a) "
        
        # Email Thread Relation
        if msgIDParent != "None":
            cypher += "MERGE (ePar:Email {id:{props}.parentId}) "
            cypher += "CREATE UNIQUE (e)-[:InReplyTo]->(ePar), (ePar)-[:Reply]->(e) "
        
        # Email Thread References
        refs = []
        msgRefs = email.utils.getaddresses(email_msg.get_all('References', []))
        for msgIDRef in msgRefs:
            msgIDRef = msgIDRef[1].strip("<>")
            refs.append(msgIDRef)
        if len(refs):
            props['refs'] = refs
            cypher += "FOREACH (ref in {refs} | MERGE (eRef:Email {id:ref}) CREATE UNIQUE (e)-[:Refs]->(eRef)) "
    
        # Add TO relations
        tos = []
        msgTo = email.utils.getaddresses(email_msg.get_all('To', ['']))
        msgXTo = email_msg.get_all('X-To', [''])
        for msg,msgX in itertools.izip_longest(msgTo,msgXTo,fillvalue=''):
            if len(msg) > 0:
                tos.append(str.lower(msg[1]))
            _collect_names(msg, msgX)
        if len(tos):
            props['tos'] = tos
            cypher += "FOREACH (to in {tos} | MERGE (aTo:Actor {email:to}) CREATE UNIQUE (e)-[:TO]->(aTo)) "
    
        # Add CC relations
        ccs = []
        msgCC = email.utils.getaddresses(email_msg.get_all('Cc', ['']))
        msgXCC = email_msg.get_all('X-Cc', [''])
        for msg,msgX in itertools.izip_longest(msgCC,msgXCC,fillvalue=''):
            if len(msg) > 0:
                ccs.append(str.lower(msg[1]))
            _collect_names(msg,msgX)
        if len(ccs):
            props['ccs'] = ccs
            cypher += "FOREACH (cc in {ccs} | MERGE (aCc:Actor {email:cc}) CREATE UNIQUE (e)-[:CC]->(aCc)) "
        
        # Add BCC relations
        bccs = []
        msgBCC = email.utils.getaddresses(email_msg.get_all('bcc', []))
        msgXBCC = email_msg.get_all('X-bcc', [])
        for msg,msgX in itertools.izip_longest(msgBCC,msgXBCC,fillvalue=''):
            if len(msg) > 0:
                bccs.append(str.lower(msg[1]))
            _collect_names(msg,msgX)
        if len(bccs):
            props['bccs'] = bccs
            cypher += "FOREACH (bcc in {bccs} | MERGE (aBcc:Actor {email:bcc}) CREATE UNIQUE (e)-[:BCC]->(aBcc)) "
    
        batch.append(cypher, props)
 
    except Exception, e:
        print e
        pass    

    return


def _collect_names(msgAddr, msgXAddr):
    global g_names
    
    if msgAddr is None or len(msgAddr) == 0:
        return
    
    msgEmail = str.lower(msgAddr[1])
    
    msgName = _get_decoded(msgAddr[0])
    if len(msgName) == 0:
        msgName = _get_decoded(msgXAddr)
            
    msgName = msgName.lower()
    msgName = msgName.replace(msgEmail,'').replace('()', '').replace('to:', '').replace('cc:', '')
    msgName = msgName.strip(" \"',<>").title()
    msgName = " ".join(msgName.split())
    msgName = " ".join(msgName.split(", ")[::-1])
    
    # Update name dictionary
    if len(msgName) > 0 and msgName != 'None':
        names = g_names.get(msgEmail, {msgName:0})
        count = names.get(msgName, 0)
        names[msgName] = count + 1
        g_names[msgEmail] = names

    return


def _add_names_to_db():
    global g_names

    txRead = g_session.create_transaction()
    txWrite = g_session.create_transaction()
    
    t0 = time.time()
    sys.stdout.write("Updating " + str(len(g_names)) + " names... ")
    try:
        emails = []
        for msgEmail, msgNames in g_names.iteritems():
            emails.append(msgEmail)

        # actor Node:names[] property
        query_str = "MATCH (n:Actor) WHERE n.email IN {emails} return n"
        txRead.append(query_str, {"emails":emails})
        results = txRead.execute()
            
        for record in results[0]:
            n = record['n']
            
            msgEmail = n['email']
            msgNames = g_names[msgEmail]
            
            names = {}
            s = n['names']
            if s is not None and len(s) > 0:
                names = json.loads(s) 

            # Update node's name dictionary
            for name in msgNames:
                if len(name) > 0 and name != 'None':
                    count_old = names.get(name, 0)
                    count_new = msgNames.get(name, 1)
                    names[name] = count_old + count_new

            bestName = max(names, key=names.get)
            jnames = json.dumps(names, ensure_ascii=False)
            txWrite.append("MATCH (n:Actor) WHERE id(n) = {id} SET n.name={name}, n.names={names}", {"id":n._id, "name":bestName, "names":jnames})

        g_names.clear()
        
    except Exception, e:
        print e
        pass    

    try:                
        txWrite.commit()
    except Exception, e:
        print e
        pass
        
    t1 = time.time()
    sys.stdout.write(str(t1-t0) + " seconds\n")
    return


def _get_decoded(strIn):
    strOut = strIn
    
    try:
        decVal = email.Header.decode_header(strIn)
        if not decVal[0][1] == None:
            strOut = unicode(decVal[0][0], decVal[0][1])
        else:
            strOut = unicode(decVal[0][0], "utf-8", errors='replace')
    except Exception, e:
        print e
        pass

    return strOut

