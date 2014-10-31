#!/usr/bin/python
import sys
from ui import app

if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = str(sys.argv[1])
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        bDebug = bool(sys.argv[3])

    app.run(debug=True, use_reloader=True, threaded=True, port=8080, host='192.168.1.100')

