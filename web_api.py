#!/usr/bin/python
import sys
from flask import Flask, jsonify, request
import query_1
import contact_list
import contact_info
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



if __name__ == '__main__':
    global g_graph
    global g_graph_index

    neo4j_conn.connect()

    app.run(debug = True)


