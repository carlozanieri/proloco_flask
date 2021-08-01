#WSGIDaemonProcess proloco_flask threads=5
#WSGIScriptAlias / /srv/http/proloco_flask/app.wsgi

#<Directory /srv/http/proloco_flask/>
#    WSGIProcessGroup flask_project
#    WSGIApplicationGroup %{GLOBAL}
#    Order deny,allow
#    Allow from all
#</Directory>
import create_app
application = create_app()
##APP_CONFIG = "/srv/http/proloco_flask/__init__.py "


#Load the application
from paste.deploy import loadapp
application = loadapp('config:%s' % APP_CONFIG)
