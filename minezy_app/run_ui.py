#!/usr/bin/python
from ui import app

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, threaded=True, port=8080, host='192.168.1.100')


