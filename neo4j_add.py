import sys
import ast
import email
import email.utils
import itertools
import neo4j_conn
from py2neo import neo4j, node, rel
from numpy.polynomial.polyutils import RankWarning

global g_names
global g_batch

def init():
    global g_names
    
    neo4j_conn.connect()
    
    g_names = {}
    return

def complete():
    _add_names_to_db()
    return

def batch_start():
    global g_batch
    
    g_batch = neo4j.WriteBatch(neo4j_conn.g_graph)
    return

def batch_commit():
    global g_batch
    
    g_batch.submit()
    _add_names_to_db()
    return

def add_to_db(email_msg):
    try:
        msgSubject = email.Header.decode_header(email_msg['Subject'])[0][0].encode("utf8")
        msgDate = email.Header.decode_header(email_msg['Date'])[0][0].encode("utf8")
        msgID = email.Header.decode_header(email_msg['Message-ID'])[0][0].encode("utf8")
        msgIDParent = email.Header.decode_header(email_msg['In-Reply-To'])[0][0].encode("utf8")
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
        
        # Add From Contact
        msgFrom = email.utils.getaddresses(email_msg.get_all('From', ['']))
        msgXFrom = email_msg.get_all('X-From', [''])
        nodeFrom = _get_contact(msgFrom[0], msgXFrom[0])
               
        # Add Email
        nodeEmail = _get_email(msgID)
        nodeEmail.set_properties({"id":msgID, "subject":msgSubject, "date":msgDate, "timestamp":timestamp})
        g_batch.get_or_create_path(nodeFrom, 'Sent', nodeEmail)
        g_batch.get_or_create_path(nodeEmail, 'SentBy', nodeFrom)
        
        # Email Thread Relation
        if msgIDParent != "None":
            nodeParent = _get_email(msgIDParent)
            g_batch.get_or_create_path(nodeEmail, 'InReplyTo', nodeParent)
            g_batch.get_or_create_path(nodeParent, 'Reply', nodeEmail)
        
        # Email Thread References
        msgRefs = email.utils.getaddresses(email_msg.get_all('References', []))
        for msgIDRef in msgRefs:
            msgIDRef = msgIDRef[1].strip("<>")
            nodeRef = _get_email(msgIDRef)
            g_batch.get_or_create_path(nodeEmail, 'Refs', nodeRef)


        # Add TO relations
        msgTo = email.utils.getaddresses(email_msg.get_all('To', []))
        msgXTo = email_msg.get_all('X-To', [])
        for msg,msgX in itertools.izip_longest(msgTo,msgXTo):
            n = _get_contact(msg, msgX)
            g_batch.get_or_create_path(nodeEmail, 'TO', n)

        # Add CC relations
        msgCC = email.utils.getaddresses(email_msg.get_all('Cc', []))
        msgXCC = email_msg.get_all('X-Cc', [])
        for msg,msgX in itertools.izip_longest(msgCC,msgXCC):
            n = _get_contact(msg,msgX)
            g_batch.get_or_create_path(nodeEmail, 'CC', n)
        
        # Add BCC relations
        msgBCC = email.utils.getaddresses(email_msg.get_all('bcc', []))
        msgXBCC = email_msg.get_all('X-bcc', [])
        for msg,msgX in itertools.izip_longest(msgBCC,msgXBCC):
            n = _get_contact(msg,msgX)
            g_batch.get_or_create_path(nodeEmail, 'BCC', n)

    except Exception, e:
        print e
        pass    

    return


def _get_contact(msgAddr, msgXAddr):
    global g_names
    
    if msgAddr is None:
        return
    
    msgEmail = str.lower(msgAddr[1])
    
    msgName = email.Header.decode_header(msgAddr[0])[0][0]
    if len(msgName) == 0:
        msgName = email.Header.decode_header(msgXAddr)[0][0]
    msgName = msgName.lower().replace(msgEmail,'')
    msgName = msgName.replace('()', '')
    msgName = msgName.replace('to:', '')
    msgName = msgName.replace('cc:', '')
    msgName = msgName.strip(" \"',<>").title().encode("utf8")
    msgName = " ".join(msgName.split())
    msgName = " ".join(msgName.split(", ")[::-1])
    
    # Contact Node
    nodeList = neo4j_conn.g_graph_index.get("contact", msgEmail)
    if len(nodeList) == 0:
        print "New contact: " + msgEmail
        nodeList = neo4j_conn.g_graph.create(node(email=msgEmail))
        nodeRet = nodeList[0]
        nodeRet.set_labels("Contact")
        neo4j_conn.g_graph_index.add('contact', nodeRet['email'], nodeRet)
    elif len(nodeList) == 1:
        nodeRet = nodeList[0]
    else:
        nodeRet = nodeList[0]
    
    # Update name dictionary
    if len(msgName) > 0 and msgName != 'None':
        names = g_names.get(msgEmail, {msgName:0})
        count = names.get(msgName, 0)
        names[msgName] = count + 1
        g_names[msgEmail] = names
    
    return nodeRet


def _get_email(msgID):
    nodeList = neo4j_conn.g_graph_index.get("email", msgID)
    if len(nodeList) == 0:
        nodeRet, = neo4j_conn.g_graph.create(node({"id":msgID}))
        nodeRet.set_labels("Email")
        neo4j_conn.g_graph_index.add('email', msgID, nodeRet)
    else:
        nodeRet = nodeList[0]
                    
    return nodeRet

    
def _add_names_to_db():
    global g_names

    print "Updating " + str(len(g_names)) + " names..."    
    # Contact Node:names[] property
    for msgEmail, msgNames in g_names.iteritems():
        nodeList = neo4j_conn.g_graph_index.get("contact", msgEmail)
        if len(nodeList) > 0:
            n = nodeList[0]
            
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
        
            n['name'] = bestName
            n['names'] = str(names)
            
    g_names.clear()
    return

    
    
