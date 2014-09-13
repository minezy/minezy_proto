#!/usr/bin/python
import os
import os.path
import sys
import imaplib
import email
import email.utils
import itertools
from multiprocessing import Pool


def dir_contents(path):
    files = []
    folders = []
    try:
        contents = os.listdir(path)
        for i, item in enumerate(contents):
            if os.path.isfile(path + '/' + contents[i]):
                files += [path + '/' + item]
            elif os.path.isdir(path + '/' + contents[i]):
                folders += [path + '/' + item]
    except:
        pass
    return files, folders

def load_folder(folder):
    print "Examining folder: " + folder
    files,folders = dir_contents(folder)
    
    count = 0
    
    try:
        if len(files) > 0:
            with open(folder + "/neo4j.csv", "w") as outfile:
                outfile.write("msgId\tmsgIdParent\tmsgRefs\tmsgDate\tmsgTimeStamp\tmsgFrom\tmsgTo\tmsgCc\tmsgBcc\tmsgSubject\n")
            
                for file in files:
                    load_file(outfile, file)
                    count += 1
                    #print str(count) + " of " + str(len(files))
            
    except Exception, e:
        print e
        pass
    
       
    for folder in folders:
        load_folder(folder)

    return 


def load_file(outfile, file):
    #print "\t" + file
    
    try:
        with open(file) as f:
            raw_email = f.read()
            email_message = email.message_from_string(raw_email)
            add_to_file(outfile, email_message)
            
    except Exception, e:
        print e
        pass

    return

def add_to_file(outfile, email_msg):
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
        msgXFrom = email_msg.get_all('X-From', [])
        fromEmail,fromName = _get_contact(msgFrom[0], msgXFrom[0])
               
        # Email Thread References
        msgIDRefs = None
        msgRefs = email.utils.getaddresses(email_msg.get_all('References', []))
        for msgIDRef in msgRefs:
            if msgIDRefs is not None:
                msgIDRefs += ","
            msgIDRefs += msgIDRef[1].strip("<>")

        # Add TO relations
        toEmails = None
        toNames = None
        msgTo = email.utils.getaddresses(email_msg.get_all('To', []))
        msgXTo = email_msg.get_all('X-To', [])
        for msg,msgX in itertools.izip_longest(msgTo,msgXTo):
            toEmail,toName = _get_contact(msg, msgX)
            if toEmails is not None:
                toEmails += ","
                toEmails += toEmail
            else:
                toEmails = toEmail

        # Add CC relations
        ccEmails = None
        ccNames = None
        msgCC = email.utils.getaddresses(email_msg.get_all('Cc', []))
        msgXCC = email_msg.get_all('X-Cc', [])
        for msg,msgX in itertools.izip_longest(msgCC,msgXCC):
            ccEmail,ccNames = _get_contact(msg,msgX)
            if ccEmails is not None:
                ccEmails += ","
                ccEmails += ccEmail
            else:
                ccEmails = ccEmail
        
        # Add BCC relations
        bccEmails = None
        bccNames = None
        msgBCC = email.utils.getaddresses(email_msg.get_all('bcc', []))
        msgXBCC = email_msg.get_all('X-bcc', [])
        for msg,msgX in itertools.izip_longest(msgBCC,msgXBCC):
            bccEmail,bccNames = _get_contact(msg,msgX)
            if bccEmails is not None:
                bccEmails += ","
                bccEmails += bccEmail
            else:
                bccEmails = bccEmail
               
        outfile.write(msgID + "\t")
        outfile.write(str(msgIDParent) + "\t")
        outfile.write(str(msgIDRefs) + "\t")
        outfile.write(str(msgDate) + "\t")
        outfile.write(str(timestamp) + "\t")
        outfile.write(fromEmail + "\t")
        outfile.write("\"" + str(toEmails) + "\"\t")
        outfile.write("\"" + str(ccEmails) + "\"\t")
        outfile.write("\"" + str(bccEmails) + "\"\t")
        outfile.write("\"" + msgSubject + "\"")
        outfile.write('\n')
        
    except Exception, e:
        print e
        pass    

    return    

def _get_contact(msgAddr, msgXAddr):
    global g_names
    
    if msgAddr is None:
        return None,None
    
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
    
    return msgEmail,msgName


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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <root_dir>"
        exit(1)

    files,folders = dir_contents(sys.argv[1])
    
    p = Pool(processes=6)
    p.map(load_folder, folders)
    
    print "All Done"
    