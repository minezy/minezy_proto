#!/usr/bin/python
import sys
import imaplib
import email
import email.utils
import neo4j_conn
from py2neo import neo4j, node, rel

import ewsclient
import suds.client
import logging
from suds.transport.https import WindowsHttpAuthenticated



if __name__ == '__main__':
#    if len(sys.argv) != 4:
#        print "Usage: " + sys.argv[0] + " <mailhost> <login> <password>"
#        exit(1)

    neo4j_conn.connect()
    
    email = 'paul@gracenote.com'
    domain = 'mailhost.gracenote.com'
    username = r'pquinn'
    password = 'pq$cddb21'
    
    transport = WindowsHttpAuthenticated(username=username,password=password)
    client = suds.client.Client("https://%s/EWS/Services.wsdl" % domain,transport=transport,plugins=[ewsclient.AddService()])
    
    print client
    
    