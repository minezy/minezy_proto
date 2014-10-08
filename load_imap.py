#!/usr/bin/python
import sys
import time
import imaplib
import email
import multiprocessing
from neo4j_loader import neo4jLoader


def parser_worker(headerQ, loaderQ):
    try:
        while True:
            header = headerQ.get()
            if header is None:
                headerQ.task_done()
                break

            if type(header) == tuple:
                raw_hdr = header[1]
                email_msg = email.message_from_string(raw_hdr)
                loaderQ.put( (email_msg, header[0]) )
            
            headerQ.task_done()
            
    except Exception, e:
        print e
        pass

    return


def loader_worker(folderName, headerQ,msgQ):
    msgQ.put("Logging into " + sys.argv[1] + ": " + sys.argv[2] + "...")
    mail = imaplib.IMAP4_SSL(sys.argv[1],port=993)
    mail.login(sys.argv[2], sys.argv[3])

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
                headerQ.put(header)
                count += 1
            
        msgQ.put(folderName + ": " + str(count) + " of " + str(len(id_list)))
        
    return


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Usage: " + sys.argv[0] + " <mailhost> <login> <password>"
        exit(1)

    t0 = time.time()
    loader = neo4jLoader(sys.argv[2], sys.argv[1]) # login is account for DB

    imapFolders = [
               #"INBOX",
               #"INBOX.Sent",
               #"INBOX.old-messages"
               "INBOX",
               "[Gmail]/Sent Mail"
               ]

    numProcs = 4
    
    if len(sys.argv) > 1:
        # using multiprocessing and generator 'traverse_dir' to speed things up
        msgQ = multiprocessing.Queue(100)
        headerQ = multiprocessing.JoinableQueue(1000)
        loaderQ = multiprocessing.JoinableQueue(1000*numProcs)
        
        loaderProcs = []
        parserProcs = []

        for folderName in imapFolders:
            p = multiprocessing.Process(target=loader_worker, args=(folderName,headerQ,msgQ))
            loaderProcs.append(p)
            p.start()
            
        for i in range(numProcs):
            p = multiprocessing.Process(target=parser_worker, args=(headerQ,loaderQ))
            parserProcs.append(p)
            p.start()
        
        while any([p.is_alive() for p in loaderProcs]):
            try:
                while True:
                    try:
                        msg = msgQ.get_nowait()
                        loader.msg(msg)
                    except:
                        pass
                    
                    item = loaderQ.get_nowait()
                    loader.add(item[0], item[1])
                    loaderQ.task_done()
            except:
                pass
                
        for p in loaderProcs:                
            p.join()
            
        for i in range(len(parserProcs)):
            headerQ.put(None)
        headerQ.join()

        try:
            while True:
                item = loaderQ.get_nowait()
                loader.add(item)
                loaderQ.task_done()
        except Exception,e:
            pass

        loaderQ.join()

    loader.complete()
    t1 = time.time()
    
    print "All Done ("+str(t1-t0) + " seconds)"
    
