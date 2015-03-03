import logging
import os
from ui import app
from flask import render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['pst','psd','mov','mp4'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET'])
def hello():
    #app.logger.info(request.headers['Host'])
    return render_template('www.html')


@app.route("/enron/", methods=['GET'])
def appui():
    #app.logger.info(request.headers['Host'])
    site = render_template('ui.html',port=5001,page='enron')
    return site

@app.route("/jebbush/", methods=['GET'])
def appuibush():
    #app.logger.info(request.headers['Host'])
    site = render_template('ui.html',port=5002,page='bush')
    return site






#@app.route('/upload/', methods=['GET','POST'])
#def upload_file():
#    app.logger.info(request.method)
#    if request.method == 'POST':
#        file = request.files['file']
#        if file and allowed_file(file.filename):
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#            return UPLOAD_FOLDER + '/' + filename
#    return '0'
