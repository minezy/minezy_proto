#!/usr/bin/python
import sys
import imaplib
import email
import email.utils
from py2neo import neo4j, node, rel

global g_email_address
global g_email_password
global g_email_server
global g_graph;
global g_graph_index;

global g_names

def get_contact(msgAddr):
    global g_graph
    global g_graph_index
    global g_names
    
    msgEmail = str.lower(msgAddr[1])
    
    msgName = email.Header.decode_header(msgAddr[0])[0][0]
    msgName = msgName.lower().replace(msgEmail,'')
    msgName = msgName.replace('()', '')
    msgName = msgName.replace('to:', '')
    msgName = msgName.replace('cc:', '')
    msgName = msgName.strip(" ',<>").title().encode("utf8")
    msgName = " ".join(msgName.split())
    msgName = " ".join(msgName.split(", ")[::-1])
    
    # Contact Node
    nodeList = g_graph_index.get("contact", msgEmail)
    if len(nodeList) == 0:
        print "New contact: " + msgEmail
        nodeList = g_graph.create(node(email=msgEmail))
        nodeRet = nodeList[0]
        nodeRet.set_labels("Contact")
        g_graph_index.add('contact', nodeRet['email'], nodeRet)
    elif len(nodeList) == 1:
        nodeRet = nodeList[0]
    else:
        nodeRet = nodeList[0]
    
    # Update name dictionary
    if len(msgName) > 0:
        names = g_names.get(msgEmail, {msgName:0})
        count = names.get(msgName, 0)
        names[msgName] = count + 1
        g_names[msgEmail] = names
    
    return nodeRet


def get_email(msgID):
    
    nodeList = g_graph_index.get("email", msgID)
    if len(nodeList) == 0:
        nodeRet, = g_graph.create(node({"id":msgID}))
        nodeRet.set_labels("Email")
        g_graph_index.add('email', msgID, nodeRet)
    else:
        nodeRet = nodeList[0]
                    
    return nodeRet

    
def add_to_db(batch, email_msg):
    global g_graph
    global g_graph_index
    
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
        msgFrom = email.utils.getaddresses(email_msg.get_all('From', []))
        nodeFrom = get_contact(msgFrom[0])
               
        # Add Email
        nodeEmail = get_email(msgID)
        nodeEmail.set_properties({"id":msgID, "subject":msgSubject, "date":msgDate, "timestamp":timestamp})
        batch.get_or_create_path(nodeFrom, 'Sent', nodeEmail)
        batch.get_or_create_path(nodeEmail, 'SentBy', nodeFrom)
        
        # Email Thread Relation
        if msgIDParent != "None":
            nodeParent = get_email(msgIDParent)
            batch.get_or_create_path(nodeEmail, 'InReplyTo', nodeParent)
            batch.get_or_create_path(nodeParent, 'Reply', nodeEmail)
        
        # Email Thread References
        msgRefs = email.utils.getaddresses(email_msg.get_all('References', []))
        for msgIDRef in msgRefs:
            msgIDRef = msgIDRef[1].strip("<>")
            nodeRef = get_email(msgIDRef)
            batch.get_or_create_path(nodeEmail, 'Refs', nodeRef)


        # Add TO relations
        msgTo = email.utils.getaddresses(email_msg.get_all('To', []))
        for msg in msgTo:
            n = get_contact(msg)
            batch.get_or_create_path(nodeEmail, 'TO', n)

        # Add CC relations
        msgCC = email.utils.getaddresses(email_msg.get_all('Cc', []))
        for msg in msgCC:
            n = get_contact(msg)
            batch.get_or_create_path(nodeEmail, 'CC', n)
        
        # Add BCC relations
        msgBCC = email.utils.getaddresses(email_msg.get_all('bcc', []))
        for msg in msgBCC:
            n = get_contact(msg)
            batch.get_or_create_path(nodeEmail, 'BCC', n)

    except Exception, e:
        print e
        pass    

    return

def add_names_to_db():
    global g_graph
    global g_graph_index

    # Contact Node:names[] property
    for msgEmail, msgNames in g_names.iteritems():
        print msgEmail
        for name, count in msgNames.iteritems():
            print name + " : " + str(count)

        bestName = max(msgNames, key=msgNames.get)
        
        nodeList = g_graph_index.get("contact", msgEmail)
        if len(nodeList) > 0:
            n = nodeList[0]
            n['name'] = bestName
            n['names'] = str(msgNames)
            
    return    

def scan_email_folder(mail, folderName):
    # Out: list of "folders" aka labels in gmail.
    mail.select(folderName) # connect to inbox.
    result, data = mail.uid('search', None, "ALL")
     
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string

    count = 0
    while count < len(id_list):   
        print "Fetching headers..."
        idfetch = ','.join(id_list[count:count+100])
        result, headers = mail.uid('fetch', idfetch, "(BODY.PEEK[HEADER])") 
        print "Done"
        
        batch = neo4j.WriteBatch(g_graph)
  
        try:
            for header in headers:
                if type(header) == tuple:
                    raw_hdr = header[1]
                    email_message = email.message_from_string(raw_hdr)
                    add_to_db(batch, email_message)
                    count += 1
                    print str(count) + " of " + str(len(id_list))

        except Exception, e:
            print e
            pass
        
        finally:
            print "Writing batch..."
            results = batch.submit()
            print "Done"

    return


if __name__ == '__main__':
    if len(sys.argv) != 4:
    	print "Usage: " + sys.argv[0] + " <mailhost> <login> <password>"
    	exit(1)

    print "Connect to Neo4j..."
    g_graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    g_graph_index = g_graph.get_or_create_index(neo4j.Node, "Nodes")
    print "OK"

    g_email_server = sys.argv[1]
    g_email_address = sys.argv[2]
    g_email_password = sys.argv[3]

    g_names = {}

    print "Logging into " + g_email_server + ": " + g_email_address + "..."
    mail = imaplib.IMAP4_SSL(g_email_server,port=443)
    print "Connected. Sending login..."
    mail.login(g_email_address, g_email_password)
    print mail.list()

    scan_email_folder(mail, "INBOX")
    scan_email_folder(mail, "INBOX.Sent")
    scan_email_folder(mail, "INBOX.old-messages")

    add_names_to_db()

    print "All Done"

   
