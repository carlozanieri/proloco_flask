#!/usr/bin/env python
"""
Flask application that receives uploaded content from browser

"""
import sys
import os
import tempfile
import flask
from flask import request
from flask import flash, render_template, redirect, url_for, session
# Python2
# import StringIO
from io import StringIO
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_login import login_required
from werkzeug.utils import secure_filename
from Connect import Connect
# whitelist of file extensions
##UPLOAD_FOLDER = '/srv/http/proloco_flask/static/img'
##UPLOAD_FOLDER = request.form['uploaddir']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = flask.Flask(__name__, static_folder="static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['MYSQL_HOST'] = 'linuxmugello.net'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'trex39'
app.config['MYSQL_DB'] = 'prolocogest'
mysql = MySQL(app)
@app.errorhandler(OSError)
def handle_oserror(oserror):
    """ Flask framework hooks into this function is OSError not handled by routes """
    response = flask.jsonify({"message":StringIO(str(oserror)).getvalue()})
    response.status_code = 500
    return response

def allowed_file(filename):
    """ whitelists file extensions for security reasons """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/home/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return flask.render_template('master.xhtml', username=session['username'], pagina=Connect.body("", "chisiamo"), luogo="index",menu=Connect.menu(""), submenu=Connect.submnu("") )
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)
# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return flask.render_template('master.xhtml', luogo="index", pagina=Connect.body("", "index"), tempdir="/srv/http/proloco_flask/static/img/", menu=Connect.menu(""), submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/profile/')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/ins_manifesta/', methods=['GET', 'POST'])
def ins_manifesta():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            multiple_upload()
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    if 'loggedin' in session:
        return render_template('ins_manifestazioni.html', msg=msg, tempdir="/srv/http/proloco_flask/static/img/", menu=Connect.menu(""), submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))
    else:
        msg = 'devi registrarti per inserire contenuti'
        return render_template('index.html', msg=msg)
@app.route("/")
def entry_point():
    """ simple entry for test """
    return flask.render_template('master.xhtml', luogo="index", pagina=Connect.body("", "index"), tempdir="/srv/http/proloco_flask/static/img/", menu=Connect.menu(""), submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))

@app.route("/master")
def master():
    """ simple entry for test """
    return flask.render_template('master.html',  tempdir="/srv/http/proloco_flask/static/img/", menu=Connect.menu(""), submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))

@app.route('/sanpiero')
def sanpiero():
        """Handle the front-page."""


        return flask.render_template('master.xhtml', pagina = Connect.body("", "sanpiero"),luogo = "sanpiero",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/mugello')
def mugello():
        """Handle the front-page."""
        return flask.render_template('master.xhtml', pagina = Connect.body("", "mugello"),luogo = "mugello",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/chisiamo')
def chisiamo():

    return flask.render_template('master.xhtml', pagina=Connect.body("", "chisiamo"), luogo="index",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/menu')
def menu():

    return flask.render_template('menu.xhtml', username=session['username'], pagina=Connect.body("", "menu"), luogo="index",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/upload_form')
def upload_form():
    """ show upload form with multiple scenarios """
    return flask.render_template('upload_form.html', pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu(""))

@app.route('/slide', methods=["GET", "POST"])
def slide():
    luogo = request.args['luogo']
    return flask.render_template('nivo.xhtml', luogo=luogo, slider=Connect.slider("", luogo))

@app.route('/news-slider')
def news():
    return flask.render_template('news-slider.xhtml', pagina=Connect.body("", "sanpiero"), manifestazione="news")

@app.route('/upload')
def upload():

    return flask.render_template('upload_form.html', pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/arrivare')
def arrivare():

    return flask.render_template('comearrivare.xhtml', pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("") )
@app.route('/newss')
def newss():
    return flask.render_template('news.xhtml', pagina=Connect.body("", "sanpiero"), manifestazione="news", news=Connect.news("") )

@app.route('/news_one')
def news_one():
        titolo = request.args['titolo']
        id = request.args['id']
        """Handle the front-page."""
        return flask.render_template('news_one.xhtml', news=Connect.news_one("", titolo, id), pagina=Connect.body("", "sanpiero"), titolo=titolo, id=id)

@app.route('/manifestazioni')
def manifestazioni():
    return flask.render_template('manifesta.xhtml', username=session['username'], titolo="Manifestazioni", per='5%', go="more", pagina=Connect.body("", "sanpiero"), manifestazione="manifestazioni", news=Connect.manifesta(""),menu=Connect.menu(""), submenu=Connect.submnu("") )

@app.route('/manifestazioni_one')
def manifestazioni_one():
        titolo = request.args['titolo']
        id = request.args['id']
        """Handle the front-page."""
        return flask.render_template('manifesta.xhtml', username=session['username'], per='30%', go="back", news=Connect.manifesta_one("", titolo, id), pagina=Connect.body("", "sanpiero"), titolo=titolo, id=id,menu=Connect.menu(""), submenu=Connect.submnu(""))

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
        return flask.redirect(flask.url_for("upload_form"), pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu(""))

    if filename is None or filename=='':
        add_flash_message("did not sense filename in form action")
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    if not allowed_file(filename):
        add_flash_message("not going to process file with extension " + filename)
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    print("Total Content-Length: " + flask.request.headers['Content-Length'])
    fileFullPath = os.path.join(app.config[request.form['uploaddir']], filename)

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
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    print("")
    add_flash_message("SUCCESS uploading single file: " + filename)
    return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))


@app.route("/multipleupload", methods=["GET", "POST", "PUT"])
def multiple_upload(file_element_name="files[]"):
    ###upload_folder = request.form['uploaddir']
    UPLOAD_FOLDER = request.form['uploaddir']
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
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    # files will be materialized as soon as we touch request.files,
    # so check for errors right up front
    try:
        flask.request.files

    except OSError as e:
        print("ERROR ON INITIAL TOUCH OF request.files")
        add_flash_message("ERROR materializing files to disk: " + StringIO(str(e)).getvalue())
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    # must have <input type="file"> element
    if file_element_name not in flask.request.files:
        add_flash_message('No files uploaded')
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    # get list of files uploaded
    files = flask.request.files.getlist(file_element_name)

    # if user did not select file, filename will be empty
    if len(files)==1 and files[0].filename == '':
        add_flash_message('No selected file')
        return flask.redirect(flask.url_for("upload_form", pagina=Connect.body("", "upload"), luogo="upload",menu=Connect.menu(""), submenu=Connect.submnu("")))

    # loop through uploaded files, saving
    for ufile in files:
        try:
            filename = secure_filename(ufile.filename)
            UPLOAD_FOLDER = request.form['uploaddir']
            if allowed_file(filename):
                print("uploading file {} of type {}".format(filename, ufile.content_type))
                ##ufile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ufile.save(os.path.join(UPLOAD_FOLDER , filename))

                #ufile.save(request.form['uploaddir'], filename)
                flask.flash("Just uploaded: " + request.form['uploaddir'] + filename)
            else:
                add_flash_message("not going to process file with extension " + filename)
        except OSError as e:
            add_flash_message("ERROR writing file " + filename + " to disk: " + StringIO(str(e)).getvalue())

    return flask.render_template('ins_manifestazioni.html', luogo="index", pagina=Connect.body("", "index"),
                                 tempdir="/srv/http/proloco_flask/static/img/", menu=Connect.menu(""),
                                 submenu=Connect.submnu(""), submenu2=Connect.submnu2(""))

    #return flask.redirect(flask.url_for("ins_manifesta", pagina=Connect.body("", "upload"), luogo="upload", menu=Connect.menu(""), submenu=Connect.submnu("")))

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
    print("tempdir: " + "/srv/http/proloco_flask/static/img/")


    # Below error if MAX_CONTENT_LENGTH is exceeded by upload
    # [error] 11#11: *1 readv() failed (104: Connection reset by peer) while reading upstream
    #app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB limit
    app.config['CHUNK_SIZE'] = 4096

    # secret key used for flask.flash messages
    app.secret_key = 'abc123'

    # docker flask uwsgi starts itself
    if __name__ == "__main__":
        if not os.getenv("TEMP_DIR") is None:
            if os.path.isdir(os.getenv("TEMP_DIR")):
                print("Overriding tempdir for docker image")
                tempfile.tempdir = os.getenv("TEMP_DIR")
        print("tempdir: " + tempfile.gettempdir())
        app.config['UPLOAD_FOLDER'] = "static/img/manifestazioni"
        port = int(os.getenv("PORT", 8000))
        app.run(host='0.0.0.0', port=port)
