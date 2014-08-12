#!/usr/bin/env python

import sys
import imaplib
import getpass
import email
import datetime

M = imaplib.IMAP4_SSL('imap.gmail.com')

print "Enter your email address:",
email = raw_input()

try:
    M.login(email, getpass.getpass())
except imaplib.IMAP4.error:
    print "LOGIN FAILED!!! "
    sys.exit(0)
    # ... exit or deal with failure...

rv, mailboxes = M.list()
if rv == 'OK':
    print "Mailboxes:"
    
    for item in mailboxes:
    	print item