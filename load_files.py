#!/usr/bin/python
import os.path
import sys
import time
import email
from neo4j_add import neo4jLoader


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

def load_folder(loader, folder):
    print "Examining folder: " + folder
    files,folders = dir_contents(folder)
    
    count = 0
    
    try:
        for fileName in files:
            load_file(loader, fileName)
            count += 1
            if count == 1 or count % 100 == 0:
                print str(count) + " of " + str(len(files))
        if count % 100 != 0:
            print str(count) + " of " + str(len(files))
            
    except Exception, e:
        print e
        pass
    
    finally:
        loader.commit()
        
    for folder in folders:
        load_folder(loader, folder)

    return 


def load_file(loader, fileName):
    #print "\t" + file
    
    try:
        with open(fileName) as f:
            email_message = email.message_from_file(f)
            if len(email_message._headers) > 0:
                loader.add(email_message)
            
    except Exception, e:
        print e
        pass

    return
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <root_dir>"
        exit(1)

    t0 = time.time()
    loader = neo4jLoader()
    
    load_folder(loader, sys.argv[1])

    loader.complete()
    t1 = time.time()
    
    print "All Done ("+str(t1-t0) + " seconds)"
    