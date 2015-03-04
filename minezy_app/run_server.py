#!/usr/bin/python
import sys
import argparse
from minezy_api import neo4j_conn
from minezy_api import app

if __name__ == '__main__':
    global g_graph
    global g_graph_index

    parser = argparse.ArgumentParser(description='Minezy API Server')
    parser.add_argument("-host", nargs=1, default="127.0.0.1")
    parser.add_argument("-port", nargs=1, default=5001, type=int)
    parser.add_argument("-dbport", nargs=1, default=7474, type=int)
    parser.add_argument("-debug", action='store_true')
    args = parser.parse_args()
        
    neo4j_conn.connect(port=args.dbport)

    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=args.debug, threaded=True)

