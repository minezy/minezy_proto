#!/usr/bin/python
import sys
import time
import imaplib
import email
import threading
import Queue
from neo4j_loader import neo4jLoader


def _imap_load_folder(mail, folderName, loader, q):
    # Out: list of "folders" aka labels in gmail.
    mail.select(folderName) # connect to inbox.
    result, data = mail.uid('search', None, "ALL")
     
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string

    count = 0
    while count < len(id_list):
        # next batch of headers   
        idfetch = ','.join(id_list[count:count+250])
        result, headers = mail.uid('fetch', idfetch, "(BODY.PEEK[HEADER])")
         
        for header in headers:
            if type(header) == tuple:
                q.put(header)
                count += 1
            
        loader.msg(folderName + ": " + str(count) + " of " + str(len(id_list)))
        
    return


def _parse_emails(loader, q):
    global g_bReadComplete
    
    try:
        while not (g_bReadComplete and q.empty()):
            header = q.get()
            
            if type(header) == tuple:
                raw_hdr = header[1]
                email_message = email.message_from_string(raw_hdr)
                loader.add(email_message)
                
            q.task_done()
        
    except Exception, e:
        print e
        pass
    return


def launch_imap(loader, q):
    folders = [
               "INBOX",
               "INBOX.Sent",
               "INBOX.old-messages"
               #"INBOX",
               #"[Gmail]/Sent Mail"
               ]
    
    threads_read = []
    threads_parse = []
    
    # imap reading threads
    for folder in folders:
        try:
            print("Logging into " + sys.argv[1] + ": " + sys.argv[2] + "...")
            mail = imaplib.IMAP4_SSL(sys.argv[1],port=993)
            print("Connected. Sending login...")
            mail.login(sys.argv[2], sys.argv[3])
            
            t = threading.Thread(target=_imap_load_folder, args=(mail, folder, loader, q))
            threads_read.append(t)
        except:
            break
        
    # email parsing threads
    for i in range(4):
        t = threading.Thread(target=_parse_emails, args=(loader, q))
        threads_parse.append(t)
        
    for t in threads_read:
        t.start()
    for t in threads_parse:
        t.start()
                
    return threads_read, threads_parse

    
g_bReadComplete = False

if __name__ == '__main__':
    global g_bReadComplete
    
    if len(sys.argv) != 4:
        print "Usage: " + sys.argv[0] + " <mailhost> <login> <password>"
        exit(1)

    t0 = time.time()
    loader = neo4jLoader()
    q = Queue.Queue(10000)

    threads_read, threads_parse = launch_imap(loader, q)
    for thread in threads_read:
        thread.join()

    g_bReadComplete = True
    
    for thread in threads_parse:
        thread.join()
            
    loader.complete()
    t1 = time.time()
    
    print "All Done ("+str(t1-t0) + " seconds)"

   
