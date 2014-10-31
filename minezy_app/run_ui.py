#!/usr/bin/python
import sys
from ui import app

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8080
    bDebug = True
    
    if len(sys.argv) > 1:
        host = str(sys.argv[1])
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        bDebug = bool(sys.argv[3])
        
    app.run(host=host, port=port, debug=bDebug, use_reloader=bDebug, threaded=True)


