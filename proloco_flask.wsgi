#Load the application
import sys
sys.path.insert(0, '/srv/http/proloco_flask/')
from proloco_flask import app as application

#WSGIDaemonProcess proloco_flask threads=5
#WSGIScriptAlias / /srv/http/proloco_flask/app.wsgi

#<Directory /srv/http/proloco_flask/>
#    WSGIProcessGroup flask_project
#    WSGIApplicationGroup %{GLOBAL}
#    Order deny,allow
#    Allow from all
#</Directory>

##application = create_app()
##APP_CONFIG = "/srv/http/proloco_flask/__init__.py "


