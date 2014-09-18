import sys
import ast
import email
import email.utils
import itertools
import neo4j_conn
from py2neo import neo4j, node, rel
from numpy.polynomial.polyutils import RankWarning

global g_names

def init():
    global g_names
    
    neo4j_conn.connect()
    
    g_names = {}
    return

def complete():
    _add_names_to_db()
    return

def batch_start():
    batch = neo4j.WriteBatch(neo4j_conn.g_graph)
    return batch

def batch_commit(batch):
    batch.submit()
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
        cypher += "ON CREATE SET e.subject={props}.subject, e.date={props}.date, e.timestamp={props}.timestamp "
        cypher += "ON MATCH SET e.subject={props}.subject, e.date={props}.date, e.timestamp={props}.timestamp "
        # Add From Actor
        cypher += "MERGE (a:Actor {email:{props}.email}) "
        cypher += "MERGE (a)-[:Sent]->(e) "
        cypher += "MERGE (e)-[:SentBy]->(a) "
        
        # Email Thread Relation
        if msgIDParent != "None":
            cypher += "MERGE (ePar:Email {id:{props}.parentId}) "
            cypher += "MERGE (e)-[:InReplyTo]->(ePar) "
            cypher += "MERGE (ePar)-[:Reply]->(e) "
        
        # Email Thread References
        refs = []
        msgRefs = email.utils.getaddresses(email_msg.get_all('References', []))
        for msgIDRef in msgRefs:
            msgIDRef = msgIDRef[1].strip("<>")
            refs.append(msgIDRef)
        props['refs'] = refs
        cypher += "FOREACH (ref in {refs} | MERGE (eRef:Email {id:ref}) MERGE (e)-[:Refs]->(eRef)) "

        # Add TO relations
        tos = []
        msgTo = email.utils.getaddresses(email_msg.get_all('To', []))
        msgXTo = email_msg.get_all('X-To', [])
        for msg,msgX in itertools.izip_longest(msgTo,msgXTo):
            tos.append(str.lower(msg[1]))
            _collect_names(msg, msgX)
        props['tos'] = tos
        cypher += "FOREACH (to in {tos} | MERGE (aTo:Actor {email:to}) MERGE (e)-[:TO]->(aTo)) "

        # Add CC relations
        ccs = []
        msgCC = email.utils.getaddresses(email_msg.get_all('Cc', []))
        msgXCC = email_msg.get_all('X-Cc', [])
        for msg,msgX in itertools.izip_longest(msgCC,msgXCC):
            ccs.append(str.lower(msg[1]))
            _collect_names(msg,msgX)
        props['ccs'] = ccs
        cypher += "FOREACH (cc in {ccs} | MERGE (aCc:Actor {email:cc}) MERGE (e)-[:CC]->(aCc)) "
        
        # Add BCC relations
        bccs = []
        msgBCC = email.utils.getaddresses(email_msg.get_all('bcc', []))
        msgXBCC = email_msg.get_all('X-bcc', [])
        for msg,msgX in itertools.izip_longest(msgBCC,msgXBCC):
            bccs.append(str.lower(msg[1]))
            _collect_names(msg,msgX)
        props['bccs'] = bccs
        cypher += "FOREACH (bcc in {bccs} | MERGE (aBcc:Actor {email:bcc}) MERGE (e)-[:BCC]->(aBcc)) "

        batch.append_cypher(cypher, props)
 
    except Exception, e:
        print e
        pass    

    return


def _collect_names(msgAddr, msgXAddr):
    global g_names
    
    if msgAddr is None:
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

    batch = neo4j.WriteBatch(neo4j_conn.g_graph)
    
    print "Updating " + str(len(g_names)) + " names..."    
    try:
        # actor Node:names[] property
        query_str = "MATCH (n:Actor) WHERE n.email = {email} return n"
        for msgEmail, msgNames in g_names.iteritems():
            query = neo4j.CypherQuery(neo4j_conn.g_graph, query_str)
            results = query.execute(email=msgEmail)
            if len(results) > 0:
                n = results[0][0]
                
                names = {}
                s = n['names']
                if s is not None and len(s) > 0:
                    names = ast.literal_eval(s) 
    
                # Update node's name dictionary
                for name in msgNames:
                    if len(name) > 0 and name != 'None':
                        count_old = names.get(name, 0)
                        count_new = msgNames.get(name, 1)
                        names[name] = count_old + count_new
    
                bestName = max(names, key=names.get)
                batch.set_property(n, 'name', bestName)
                batch.set_property(n, 'names', str(names))

        g_names.clear()
        
    except Exception, e:
        print e
        pass    
                
    batch.submit()
    return


def _get_decoded(strIn):
    strOut = strIn
    
    try:
        decVal = email.Header.decode_header(strIn)
        if not decVal[0][1] == None:
            strOut = str.decode(decVal[0][0], decVal[0][1])
        else:
            strOut = decVal[0][0]
    except Exception, e:
        print e
        pass    

    return strOut

