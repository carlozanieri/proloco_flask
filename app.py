#!/usr/bin/env python
"""
Flask application that receives uploaded content from browser

"""
import sys
import os
import tempfile
import flask
from flask import  request
from flask import url_for
# Python2
# import StringIO
from io import StringIO
from werkzeug.utils import secure_filename
from Connect import Connect
# whitelist of file extensions
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = flask.Flask(__name__, static_folder="static")

@app.errorhandler(OSError)
def handle_oserror(oserror):
    """ Flask framework hooks into this function is OSError not handled by routes """
    response = flask.jsonify({"message":StringIO(str(oserror)).getvalue()})
    response.status_code = 500
    return response

def allowed_file(filename):
    """ whitelists file extensions for security reasons """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def entry_point():
    """ simple entry for test """
    return flask.render_template('master.xhtml', luogo="index", pagina=Connect.body("", "index"), tempdir=tempfile.gettempdir(), menu=Connect.menu(""), submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))

@app.route("/master")
def master():
    """ simple entry for test """
    return flask.render_template('master.html',  tempdir=tempfile.gettempdir(), menu=Connect.menu(""), submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))

@app.route('/sanpiero')
def sanpiero():
        """Handle the front-page."""


        return flask.render_template('master.xhtml', pagina = Connect.body("", "sanpiero"),luogo = "sanpiero",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/mugello')
def mugello():
        """Handle the front-page."""


        return flask.render_template('master.xhtml', pagina = Connect.body("", "mugello"),luogo = "mugello",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/upload_form')
def upload_form():
    """ show upload form with multiple scenarios """
    return flask.render_template('upload_form.html')

@app.route('/slide', methods=["GET", "POST"])
def slide():
    luogo = request.args['luogo']
    return flask.render_template('nivo.xhtml', luogo=luogo, slider=Connect.slider("", luogo))

@app.route('/news-slider')
def news():
    return flask.render_template('news-slider.xhtml', pagina=Connect.body("", "sanpiero"), manifestazione="news")


@app.route('/newss')
def newss():
    return flask.render_template('news.xhtml', pagina=Connect.body("", "sanpiero"), manifestazione="news", news=Connect.news("") )

@app.route("/singleuploadchunked/<filename>", methods=["POST", "PUT"])
def single_upload_chunked(filename=None):
    """Saves single file uploaded from <input type="file">, uses stream to read in by chunks

       When using direct access to flask.request.stream
       you cannot access request.file or request.form first,
       otherwise stream is already parsed and empty
       This is because of internal workings of werkzeug

       Positive test:
       curl -X POST http://localhost:8080/singleuploadchunked/car.jpg -d "@tests/car.jpg"

       Negative test (no file uploaded, no Content-Length header):
       curl -X POST http://localhost:8080/singleuploadchunked/car.jpg
       Negative test (not whitelisted file extension):
       curl -X POST http://localhost:8080/singleuploadchunked/testdoc.docx -d "@tests/testdoc.docx"
    """
    if "Content-Length" not in flask.request.headers:
        add_flash_message("did not sense Content-Length in headers")
        return flask.redirect(flask.url_for("upload_form"))

    if filename is None or filename=='':
        add_flash_message("did not sense filename in form action")
        return flask.redirect(flask.url_for("upload_form"))

    if not allowed_file(filename):
        add_flash_message("not going to process file with extension " + filename)
        return flask.redirect(flask.url_for("upload_form"))

    print("Total Content-Length: " + flask.request.headers['Content-Length'])
    fileFullPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    chunk_size = app.config['CHUNK_SIZE']
    try:
        with open(fileFullPath, "wb") as f:
            reached_end = False
            while not reached_end:
                chunk = flask.request.stream.read(chunk_size)
                if len(chunk) == 0:
                    reached_end = True
                else:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    # the idea behind this chunked upload is that large content could be persisted
                    # somewhere besides the container: S3, NFS, etc...
                    # So we use a container with minimal mem/disk, that can handle large files
                    #
                    #f.write(chunk)
                    #f.flush()
                    #print("wrote chunk of {}".format(len(chunk)))
    except OSError as e:
        add_flash_message("ERROR writing file " + filename + " to disk: " + StringIO(str(e)).getvalue())
        return flask.redirect(flask.url_for("upload_form"))

    print("")
    add_flash_message("SUCCESS uploading single file: " + filename)
    return flask.redirect(flask.url_for("upload_form"))


@app.route("/multipleupload", methods=["GET", "POST", "PUT"])
def multiple_upload(file_element_name="files[]"):
    """Saves files uploaded from <input type="file">, can be multiple files
    
       Positive Test (single file):
       curl -X POST http://localhost:8080/multipleupload -F "files[]=@tests/car.jpg"
       Positive Test (multiple files):
       curl -X POST http://localhost:8080/multipleupload -F "files[]=@tests/car.jpg" -F "files[]=@tests/testdoc.pdf"

       Negative Test (using GET method):
       curl -X GET http://localhost:8080/multipleupload
       Negative Test (no input file element):
       curl -X POST http://localhost:8080/multipleupload
       Negative Test (not whitelisted file extension):
       curl -X POST http://localhost:8080/multipleupload -F "files[]=@tests/testdoc.docx"
    """

    # must be POST/PUT
    if flask.request.method not in ['POST', 'PUT']:
        add_flash_message("Can only upload on POST/PUT methods")
        return flask.redirect(flask.url_for("upload_form"))

    # files will be materialized as soon as we touch request.files,
    # so check for errors right up front
    try:
        flask.request.files
    except OSError as e:
        print("ERROR ON INITIAL TOUCH OF request.files")
        add_flash_message("ERROR materializing files to disk: " + StringIO(str(e)).getvalue())
        return flask.redirect(flask.url_for("upload_form"))

    # must have <input type="file"> element
    if file_element_name not in flask.request.files:
        add_flash_message('No files uploaded')
        return flask.redirect(flask.url_for("upload_form"))

    # get list of files uploaded
    files = flask.request.files.getlist(file_element_name)

    # if user did not select file, filename will be empty
    if len(files)==1 and files[0].filename == '':
        add_flash_message('No selected file')
        return flask.redirect(flask.url_for("upload_form"))

    # loop through uploaded files, saving
    for ufile in files:
        try:
            filename = secure_filename(ufile.filename)
            if allowed_file(filename):
                print("uploading file {} of type {}".format(filename, ufile.content_type))
                ufile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flask.flash("Just uploaded: " + filename)
            else:
                add_flash_message("not going to process file with extension " + filename)
        except OSError as e:
            add_flash_message("ERROR writing file " + filename + " to disk: " + StringIO(str(e)).getvalue())

    return flask.redirect(flask.url_for("upload_form"))

def add_flash_message(msg):
    """Provides message to end user in browser"""
    print(msg)
    flask.flash(msg)

# from console it is the standard '__main__', but from docker flask it is 'main'
if __name__ == "__main__" or __name__ == "main":

    # docker flask image
    if __name__ == "main":
        if not os.getenv("TEMP_DIR") is None:
            if os.path.isdir(os.getenv("TEMP_DIR")):
              print("Overriding tempdir for docker image")
              tempfile.tempdir = os.getenv("TEMP_DIR")
    print("tempdir: " + tempfile.gettempdir())
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

    # Below error if MAX_CONTENT_LENGTH is exceeded by upload
    # [error] 11#11: *1 readv() failed (104: Connection reset by peer) while reading upstream
    #app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB limit
    app.config['CHUNK_SIZE'] = 4096

    # secret key used for flask.flash messages
    app.secret_key = 'abc123'

    # docker flask uwsgi starts itself
    if __name__ == "__main__":
        port = int(os.getenv("PORT", 8000))
        app.run(host='0.0.0.0', port=port)
