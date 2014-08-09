#!/usr/bin/python
import sys
from flask import Flask, jsonify, request
import query_1
import contact_list
import contact_info
import email_info
import neo4j_conn

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_versions():
    api_versions = [ { 'v1' : 'http://' + request.host + '/1' } ]
    return jsonify( { 'api_versions' : api_versions } )

@app.route('/1/', methods=['GET'])
def get_api_v1():
    apis_v1 = [
        {
            'api': '/1/load_imap/<server>/<login>/<passwd>',
            'description': 'load email from account into database'
        },

        # Contacts
        {
            'api': '/1/contacts/<start>/<count>/',
            'description': 'List contacts',
            'href': 'http://' + request.host + '/1/contacts/0/10/'
        },
        {
            'api': '/1/contacts/emailsent',
            'description': 'List contacts ordered by emails sent'
        },
        {
            'api': '/1/contacts/emailreceieved',
            'description': 'List contacts ordered by emails received'
        },
        {
            'api': '/1/contacts/senders',
            'description': 'List contacts ordered by number of others who sent to'
        },

        # Contact
        {
            'api': '/1/contact/<email>/',
            'description': 'Get contact details'
        },
        {
            'api': '/1/contact/<email1>/<email2>',
            'description': 'Get relations between email1 and email2'
        }
    ]
    return jsonify( { 'apis' : apis_v1 } )

@app.route('/1/contacts/<int:start>/<int:count>/', methods=['GET'])
def get_contacts(start, count):
    contacts = contact_list.contactList(start, count)
    return jsonify( { 'contacts' : contacts } )

@app.route('/1/contact/<email>/')
def get_contact(email):
    contact = contact_info.contactInfo(email)
    return jsonify( { 'contact' : contact } )

@app.route('/1/contact/<email>/sentTo/')
def get_contact_sentTo(email):
    resp = contact_info.contact_sentTo(email)
    return jsonify( resp )

@app.route('/1/contact/<email>/sentFrom/')
def get_contact_sentFrom(email):
    resp = contact_info.contact_sentFrom(email)
    return jsonify( resp )

@app.route('/1/contact/<email>/privateTo/')
def get_contact_privateTo(email):
    resp = contact_info.contact_privateTo(email)
    return jsonify( resp )

@app.route('/1/contact/<email>/privateFrom/')
def get_contact_privateFrom(email):
    resp = contact_info.contact_privateFrom(email)
    return jsonify( resp )

@app.route('/1/emails/<fromAddr>/to/<toAddr>/')
def get_emails_conv(fromAddr, toAddr):
    resp = email_info.email_list(fromAddr, toAddr)
    return jsonify( resp )

@app.route('/1/email/<emailId>/')
def get_email_info(emailId):
    resp = email_info.email_info(emailId)
    return jsonify( resp )

if __name__ == '__main__':
    global g_graph
    global g_graph_index

    neo4j_conn.connect()

    app.run(debug=True, use_reloader=False)


