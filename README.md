minezy_proto
============

To run Minezy:

First in stall Neo4j database (v2.0+), and have it running at localhost:7474
Then under ./minezy_api/ launch: (ensure Flask is installed)

<b>python ./run_ui.py<br>
python ./run_server.py</b>


Open browser to: localhost:8080/
You should see the Minezy title page, but there won't be anything to navigate until you load Neo4j with email data.
Do that by running:

<b>python ./load_imap.py <mail host> <email account> <password></b>

Once complete, reload localhost:8080/ and start minezying.
