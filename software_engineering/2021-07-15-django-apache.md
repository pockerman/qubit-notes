# Use Django with Apache


## Overview

In this note, I describe how to serve a Django application on a LAMP infrastructure.
You can find the application source code <a href="https://github.com/pockerman/hmmtuf_app">here</a>.


**keywords:** Django, Python, web-development, wsgi, LAMP

##  Use Django with Apache

<a href="https://www.djangoproject.com/">Django</a> is a popular web development framework for Python. I have used it a few times to develop back-end functionality
that supports various applications. In this note, I want to describe the steps I followed in order to deploy a Django backed application on a LAMP server.

To start with, the Django offcial documentation has most of the information you need <a href="https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/modwsgi/">here</a>. 
The suggested way is by using ```mod_wsgi```. The problem that I had with that was due to a problem with SQLite that the project was initially using. I had to create a virtual environment on the server and install everything under this. However, ```mod_wsgi``` only works with the version of Python it was compiled against. So if this is the case you may have to install the package in your environment. 

In the latter scenario, you need to configure the modules loaded by Apache such that it points to your installation and not the system-wide one. You can run a ```find``` command on the directory you have your virtual environments:

```
find /path/to/your/envs/ -name "mod_wsgi*.so"
```

Then you need to update ```loadmodule.conf``` (which is typically located at ```/local/apache2/etc/```) to point to the path given by ```find```.
You then need to update the ```httpd.conf``` file according to your needs. You will need to provide as a minimum the following:

```
Alias /robots.txt /path/to/mysite.com/static/robots.txt
Alias /favicon.ico /path/to/mysite.com/static/favicon.ico

Alias /media/ /path/to/mysite.com/media/
Alias /static/ /path/to/mysite.com/static/

<Directory /path/to/mysite.com/static>
Require all granted
</Directory>

<Directory /path/to/mysite.com/media>
Require all granted
</Directory>

WSGIDaemonProcess django_app_name python-home=/path/to/virtual/env/ python-path=/path/to/django/app/
WSGIProcessGroup  django_app_name
WSGIScriptAlias / /path/to/django/app/wsgi.py process-group=django_app_name
WSGIApplicationGroup %{GLOBAL}


<Directory /path/to/mysite.com/mysite>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
```

It turns out that the process is not overly complicated but it may take some time to figure out some things. 


## References

1. <a href="https://www.djangoproject.com/">Django</a>