#!/usr/bin/python
import os.path
import sys
import time
import email.parser
import multiprocessing
import traceback
from neo4j_loader import neo4jLoader

def parser_worker(fileQ, loaderQ):
    try:
        while True:
            fileName = fileQ.get()
            if fileName is None:
                fileQ.task_done()
                break
            
            rootLen = len(sys.argv[1])
            if fileName[rootLen] == '/' or fileName[rootLen] == '\\':
                rootLen += 1
            
            parser = email.parser.Parser()
            
            with open(fileName) as f:
                eFile = fileName[rootLen:]
                email_msg = parser.parse(f, headersonly=True)
                if len(email_msg._headers) > 0:
                    
                    t = email_msg._headers[0]
                    if t[1] == 'VCARD':
                        "vcard - skip"
                    elif t[1] == 'VCALENDAR':
                        "vcalendar - skip"
                    else:
                        loaderQ.put( (email_msg, eFile) )
            fileQ.task_done()
            
    except Exception, e:
        print e
        pass

    loaderQ.put(None)
    return

def traverse_dir(folder):
    for root,dirs,files in os.walk(folder):
        loader.msg("Examining folder: " + root)
        for name in files:
            yield (os.path.join(root, name))
    return

def service_loader_q(loaderQ, block, numRunning):
    try:
        while numRunning > 0:
            if (block):
                item = loaderQ.get()
            else: 
                item = loaderQ.get_nowait()

            if item == None:
                numRunning = numRunning - 1
            else:
                email_msg = item[0]
                loader.add(item[0], item[1])
    except Exception,e:
        pass

    return numRunning

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: " + sys.argv[0] + " <depot_dir> <depot_name>"
        exit(1)
    
    t0 = time.time()
    
    account = sys.argv[1].replace("\\", "/").replace("//", "/")
    name = sys.argv[2]
    loader = neo4jLoader(account, name)
    
    numProcs = 8
    numRunning = numProcs

    if len(sys.argv) > 1:
        # using multiprocessing and generator 'traverse_dir' to speed things up
        fileQ = multiprocessing.JoinableQueue(1000)
        loaderQ = multiprocessing.Queue(1000*numProcs)
        
        procs = []
        for i in range(numProcs):
            p = multiprocessing.Process(target=parser_worker, args=(fileQ,loaderQ))
            procs.append(p)
            p.start()
        
        for fileName in traverse_dir(sys.argv[1]):
            while True:
                try:
                    fileQ.put(fileName, True, 1)
                    break
                except Exception,e:
                    numRunning = service_loader_q(loaderQ, False, numRunning)

        for i in range(len(procs)):
            fileQ.put(None)

        service_loader_q(loaderQ, True, numRunning)
        fileQ.join()

    loader.complete()
    t1 = time.time()
    
    print "All Done ("+str(t1-t0) + " seconds)"
    
    