#WSGIDaemonProcess proloco_flask threads=5
#WSGIScriptAlias / /srv/http/proloco_flask/app.wsgi

#<Directory /srv/http/proloco_flask/>
#    WSGIProcessGroup flask_project
#    WSGIApplicationGroup %{GLOBAL}
#    Order deny,allow
#    Allow from all
#</Directory>
from proloco_flask import create_app
application = create_app()
##APP_CONFIG = "/srv/http/proloco_flask/__init__.py "

#Setup logging
#import logging.config
#logging.config.fileConfig(APP_CONFIG)

#Load the application
from paste.deploy import loadapp
application = loadapp('config:%s' % APP_CONFIG)
