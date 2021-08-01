#! /usr/bin/python3.9
activate_this = '/srv/http/proloco_flask/app.py'
execfile(activate_this, dict(__file__=activate_this))
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/srv/http/proloco_flask/')
from app import app as application
application.secret_key = 'proloco'

