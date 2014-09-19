#!/usr/bin/python
import sys
import time
import imaplib
import email
import email.utils
from email.parser import Parser
import neo4j_add

def scan_email_folder(mail, folderName):
    # Out: list of "folders" aka labels in gmail.
    mail.select(folderName) # connect to inbox.
    result, data = mail.uid('search', None, "ALL")
     
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string

    count = 0
    while count < len(id_list):
        # next batch of headers   
        t0 = time.time()
        sys.stdout.write("Fetching headers... ")
        
        idfetch = ','.join(id_list[count:count+500])
        result, headers = mail.uid('fetch', idfetch, "(BODY.PEEK[HEADER])")
         
        t1 = time.time()
        sys.stdout.write(str(t1-t0) + " seconds\n")
        
        batch = neo4j_add.batch_start()
        try:
            for header in headers:
                if type(header) == tuple:
                    raw_hdr = header[1]
                    email_message = email.message_from_string(raw_hdr)
                    neo4j_add.add_to_db(email_message, batch)
                    count += 1
                    if count == 1 or count % 100 == 0:
                        print str(count) + " of " + str(len(id_list))
            if count % 100 != 0:
                print str(count) + " of " + str(len(id_list))
            
        except Exception, e:
            print e
            pass
        
        finally:
            neo4j_add.batch_commit(batch)

    return


if __name__ == '__main__':
    if len(sys.argv) != 4:
    	print "Usage: " + sys.argv[0] + " <mailhost> <login> <password>"
    	exit(1)

    neo4j_add.init()

    print "Logging into " + sys.argv[1] + ": " + sys.argv[2] + "..."
    mail = imaplib.IMAP4_SSL(sys.argv[1],port=993)
    print "Connected. Sending login..."
    mail.login(sys.argv[2], sys.argv[3])
    print mail.list()

    #scan_email_folder(mail, "INBOX")
    #scan_email_folder(mail, "INBOX.Sent")
    #scan_email_folder(mail, "INBOX.old-messages")
    scan_email_folder(mail, "INBOX")
    scan_email_folder(mail, "[Gmail]/Sent Mail")

    print "All Done"

   
