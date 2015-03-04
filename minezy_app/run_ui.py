#!/usr/bin/python
import sys
import argparse
from ui import app

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Minezy API Server')
    parser.add_argument("-host", nargs=1, default="127.0.0.1")
    parser.add_argument("-port", nargs=1, default="8080", type=int)
    parser.add_argument("-debug", action='store_true')
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=args.debug, threaded=True)

