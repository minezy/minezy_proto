#!/usr/bin/python
import sys
import datetime
import time
import operator
import email
import email.utils
import math
from collections import OrderedDict
from flask import request
from py2neo import neo4j, node, rel
import neo4j_conn


def email_list(fromAddr, toAddr):
	resp = {}
	resp['from'] = { 'contact': fromAddr, 'href': 'http://' + request.host + '/1/contact/' + fromAddr }
	resp['to']   = { 'contact': toAddr,   'href': 'http://' + request.host + '/1/contact/' + toAddr }

	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (:Contact {email:'" + fromAddr + "'})-[:Sent]->(e)-[:TO]->(:Contact {email:'" + toAddr +"'}) "
		"WHERE NOT (e)-[:InReplyTo]->() "
		"RETURN e ORDER BY e.timestamp desc"
		)
	emails = []
	for record in query.stream():
		e = record[0]
		emails.append( {
			'subject': e['subject'], 
			'date': e['date'], 
			'href': 'http://' + request.host + '/1/email/' + e['id'],
			} )
	resp['emailsInitiated'] = emails

	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (:Contact {email:'" + fromAddr + "'})-[:Sent]->(e)-[:TO]->(:Contact {email:'" + toAddr +"'}) "
		"WHERE (e)-[:InReplyTo]->() "
		"RETURN e ORDER BY e.timestamp desc"
		)
	emails = []
	for record in query.stream():
		e = record[0]
		emails.append( {
			'subject': e['subject'], 
			'date': e['date'], 
			'href': 'http://' + request.host + '/1/email/' + e['id'],
			} )
	resp['emailsReplied'] = emails
	
	return resp


def email_thread(emailId):
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (e:Email {id:'" + emailId + "'}) "
		"OPTIONAL MATCH (e)-[:Reply]->(er) "
		"WITH e,er ORDER BY er.timestamp asc "
		"MATCH e-[:SentBy]->(sender) "
		"OPTIONAL MATCH e-[:TO]->(to) "
		"OPTIONAL MATCH e-[:CC]->(cc) "
		"OPTIONAL MATCH e-[:InReplyTo]->(inreplyto) "
		"RETURN e, collect(er), sender, collect(distinct to), collect(distinct cc), inreplyto"
		)
	results = query.execute()

	resp = {}
	eReplies = []
	for record in results:
		e = record[0]
		eRefs = record[1]
		s = record[2]
		to = record[3]
		cc = record[4]
		eRep = record[5]

		resp = {
			'subject': e['subject'], 
			'date': e['date'],
			'id': e['id'],
			'from': 'http://' + request.host + '/1/contact/' + s['email'],
			}

		if eRep is not None:
			resp['inreplyto'] = eRep['id']
					
		toList = []
		for t in to:
			toList.append('http://' + request.host + '/1/contact/' + t['email'])
		
		ccList = []
		for c in cc:
			ccList.append('http://' + request.host + '/1/contact/' + c['email'])
		if len(ccList) > 0:
			toList.append( {'cc': ccList } )
		
		resp['to'] = toList
		
#		for er in eRefs:
#			eThread = email_thread(er['id'])
#			if len(eThread) > 0:
#				eReplies.append(eThread)
				
	if len(eReplies) > 0:
		resp['replies'] = eReplies
			
	return resp
				
# 		"MATCH e-[:SentBy]->(sender) "
#		"OPTIONAL MATCH e-[:TO]->(to) "
#		"OPTIONAL MATCH e-[:CC]->(cc) "
	
def email_info(emailId):
	query = neo4j.CypherQuery(neo4j_conn.g_graph,
		"MATCH (e:Email {id:'" + emailId + "'}) "
		"OPTIONAL MATCH (e)-[:Refs|Reply]-(er) "
		"WITH e,er ORDER BY er.timestamp asc "
		"MATCH e-[:SentBy]->(sender) "
		"OPTIONAL MATCH e-[:TO]->(to) "
		"OPTIONAL MATCH e-[:CC]->(cc) "
		"RETURN e, collect(er), sender, collect(distinct to), collect(distinct cc)"
		)
	results = query.execute()

	resp = {}
	eReplies = []
	for record in results:
		e = record[0]
		eRefs = record[1]
		s = record[2]
		to = record[3]
		cc = record[4]

		resp = {
			'subject': e['subject'], 
			'date': e['date'],
			'id': e['id'],
			'from': 'http://' + request.host + '/1/contact/' + s['email']
			}

		toList = []
		for t in to:
			toList.append('http://' + request.host + '/1/contact/' + t['email'])
		resp['to'] = toList
		
		ccList = []
		for c in cc:
			ccList.append('http://' + request.host + '/1/contact/' + c['email'])
		resp['cc'] = ccList
		
		for er in eRefs:
			eThread = email_thread(er['id'])
			if len(eThread) > 0:
				if eThread not in eReplies:
					eReplies.append(eThread)
				
	if len(eReplies) > 0:
		resp['replies'] = eReplies
			
	return resp


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: " + sys.argv[0] + " <emailFrom> <emailTo>"
		exit(1)

	neo4j_conn.connect()

	emails = email_list(sys.argv[1], sys.argv[2])
	print str(emails)
	print

