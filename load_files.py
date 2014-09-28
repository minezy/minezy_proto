#!/usr/bin/python
import os.path
import sys
import time
import email
import multiprocessing.dummy
from neo4j_add import neo4jLoader


def dir_files(path):
    files = []
    try:
        contents = os.listdir(path)
        for i, item in enumerate(contents):
            if os.path.isfile(path + '/' + contents[i]):
                files += [path + '/' + item]
    except Exception, e:
        print e
        pass
    
    return files


def load_folder(data):
    folder = data[0]
    loader = data[1]
    
    loader.msg("Examining folder: " + folder)
    files = dir_files(folder)
    
    try:
        for fileName in files:
            load_file(loader, fileName)
    except Exception, e:
        print e
        pass
    
    return 


def load_file(loader, fileName):
    try:
        rootLen = len(sys.argv[1])
        if fileName[rootLen] == '/' or fileName[rootLen] == '\\':
            rootLen += 1
            
        with open(fileName) as f:
            eFile = fileName[rootLen:]
            email_message = email.message_from_file(f)
            if len(email_message._headers) > 0:
                loader.add(email_message, emailLink=eFile)
            
    except Exception, e:
        print e
        pass

    return
    
if __name__ == '__main__':
    "Usage: [dir] [dir] ..."
    t0 = time.time()
    loader = neo4jLoader()
    
    if len(sys.argv) > 1:
        folders = []
        for i in range(1, len(sys.argv)):
            sys.stdout.write("Gathering subfolders of " + sys.argv[i] + "... ")
            folders += [x[0] for x in os.walk(sys.argv[i])]
            sys.stdout.write(str(len(folders)) + "\n")
        data = [(folder, loader) for folder in folders]
        
        pool = multiprocessing.dummy.Pool(processes=4)
        pool.map(load_folder, data)
        pool.join()

    loader.complete()
    t1 = time.time()
    
    print "All Done ("+str(t1-t0) + " seconds)"
    
    