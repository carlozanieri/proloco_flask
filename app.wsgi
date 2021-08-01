WSGIDaemonProcess proloco_flask threads=5
WSGIScriptAlias / /srv/http/proloco_flask/app.wsgi

<Directory /srv/http/proloco_flask/>
    WSGIProcessGroup flask_project
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
</Directory>