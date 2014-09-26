#!/usr/bin/python
from minezy_api import neo4j_conn
from minezy_api import app

if __name__ == '__main__':
    global g_graph
    global g_graph_index

    neo4j_conn.connect()

    app.run(debug=True, use_reloader=True, threaded=True)


