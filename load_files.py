#!/usr/bin/python
import os
import os.path
import sys
import imaplib
import email
import email.utils
import neo4j_add


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
    
    neo4j_add.batch_start()
    count = 0
    
    try:
        for file in files:
            load_file(file)
            count += 1
            print str(count) + " of " + str(len(files))
            
    except Exception, e:
        print e
        pass
    
    finally:
        if count > 0:
            print "Writing batch..."
            neo4j_add.batch_commit()
            print "Done"
        
    for folder in folders:
        load_folder(folder)

    return 


def load_file(file):
    #print "\t" + file
    
    try:
        with open(file) as f:
            raw_email = f.read()
            email_message = email.message_from_string(raw_email)
            neo4j_add.add_to_db(email_message)
            
    except Exception, e:
        print e
        pass

    return
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <root_dir>"
        exit(1)

    neo4j_add.init()
    
    load_folder(sys.argv[1])

    neo4j_add.complete()
    print "All Done"
    