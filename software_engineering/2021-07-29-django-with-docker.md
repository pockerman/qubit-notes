# Django with Docker


## Overview

Deploying applications is never easy regardless of the provisioning one may take. Containers, however, may  solve many of the problems of application deployment. In this post, I want to describe how to containerize a minimal <a href="https://www.djangoproject.com/">django</a> application with <a href="https://www.docker.com/">docker</a>. 
I will assume that docker is already installed on yourr machine. If that is not the case, checkout the official <a href="https://www.docker.com/">docker</a> documentation.  
This post will not go really in depth. If you need more details, checkout <a href="https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/">Dockerizing Django with Postgres, Gunicorn, and Nginx</a> post. The code for this notebook can be found at <a href="https://github.com/pockerman/demo_django_with_docker">this repository</a>.


**keywords:** docker, docker-compose, containers, django, python


## Django with docker

<a href="https://www.djangoproject.com/">Django</a> is a popular web development framework for Python. I have used it a few times to develop back-end functionality
that supports various applications. In this post, I want to describe how to containerize a minimal <a href="https://www.djangoproject.com/">django</a> application with <a href="https://www.docker.com/">docker</a>.  The application won't do something really great as my goal here is to understand how to make these components work together. Thus, the application I will be looking at has two main components in terms of infrastructure. Namely,

- It uses Django to support HTTP requests/responses
- It uses MySQL for persistence

I will assume that docker is already installed on your machine. You can check the version of docker and docker-compose by typing in the terminal.

```
docker --version
docker-compose --version
```

I will also assume that Django is installed on your machine.

### Django project

Creating a simple Django project is fairly easy. Let's create a ```hello_world_django``` project. I will have the project files in the ```app``` directory. So

```
mkdir app && cd app
django-admin startproject hello_world_django .
```

The above creates the ```app``` directory and within that directory it creates the ```hello_world_django```. 

```
 ├── hello_world_django
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── manage.py
```

Let's create a ```requirements.txt``` file in the ```app``` directory with the following contents

```
Django==3.0.7
```

In order to containerize the ```hello_world_django``` project, we need to have a ```Dockerfile```.  A ```Dockerfile``` specifies overall how an image of our application should be built. So in the ```app``` directory, create a ```Dockerfile``` with the following contents

```
# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
```

The ```Dockerfile``` above, starts with an Alpine-based Docker image for Python 3.8.3. It then sets a working directory along with two environment variables:

- ```PYTHONDONTWRITEBYTECODE```: Prevents Python from writing ```pyc``` files to disc (equivalent to ```python -B``` option)
- ```PYTHONUNBUFFERED```: Prevents Python from buffering ```stdout``` and ```stderr``` (equivalent to ```python -u``` option)

Finally, it updates ```pip```, copies over the ```requirements.txt``` file, installed the dependencies, and copied over the Django project itself. 
Although we can use ```docker build``` to build our image, I will use ```docker-compose``` to do so. In the source directory, create a file called ```docker-compose.yml``` with the following contents

 ```
version: '3.8'

services:
  web:
    build: ./app
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
    ports:
      - 8000:8000
    env_file:
      - ./.env.dev

 ```

We also need one more file, namely the ```.env.dev``` file that contains the following

```
DEBUG=1
SECRET_KEY=foo
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0 [::1]

```

The file should also be placed at the root directory where the ```docker-compose.yml``` is located. We also need to update the ```settings.py``` file so that we can  retrieve these from the environment under which the application is running.

```
SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG", default=0))

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

```

Let's now build the image and check if everything works as described above. We can do so

```
docker-compose build
```

Start the container by using 

```
docker-compose up -d
```

We can view the application at http://0.0.0.0:8000/. This should display django's default landing page. So far so good. Let's now try to integrate MySQL into the mix.

## Configure MySQL

In order to add MySQL as a persistence layer for our application, we need to add a new service into ```docker-compose.yml```. This is shown below

```
version: '3.7'

services:
  web:
    build: ./app
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./app/:/usr/src/app/
    ports:
      - 8000:8000
    env_file:
      - ./.env.dev
   db:
    image: mysql:5.7
    container_name: mysql_my_django_app
    ports:
      - '3306:3306'
    environment:
      MYSQL_DATABASE: 'django_app_demo'
      MYSQL_PASSWORD: 'password'
      MYSQL_ROOT_PASSWORD: 'password'
      
   
  volumes:
    mysql_data:


```

To persist the data beyond the life of the container we configured a volume. This ```config``` will bind ```mysql_data``` to the ```"/var/lib/mysql/data/"``` directory in the container.
Note that since the default database in django is ```sqlite3```, we need to update the ```DATABASES``` entry in the ```settings.py``` file according to

```
DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"), #'django.db.backends.mysql',
        'NAME': os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3"), #'django_app_demo',
        'USER': os.environ.get("SQL_USER", "user"), #'root',
        'PASSWORD': os.environ.get("SQL_PASSWORD", "password"), #'password',
        'HOST': os.environ.get("SQL_HOST", "localhost"), #'db',
        'PORT': os.environ.get("SQL_PORT", "3306"), #3306,
    }
}
```

Similarly, we update the ```.env.dev``` file now looking like

```
DEBUG=1
SECRET_KEY=foo
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0 [::1]
SQL_ENGINE=django.db.backends.mysql
SQL_DATABASE=django_app_demo
SQL_USER=root
SQL_PASSWORD=password
SQL_HOST=db
SQL_PORT=3306
```

We also need to to install ```mysqlclient``` otherwise we get a django exception ```django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module.``` We add this in the requirements file. So the ```requirements.txt``` is now as follows

```
Django==3.0.7
mysqlclient==2.0.3
```

We now have two containers. Let's build the new image and spin the two containers

```
docker-compose up -d --build
```

Once again we can access the application at http://0.0.0.0:8000/.

### Migrations

In order to be able to persist data, we need to create the database tables. Django uses the notion of migrations in order to build and monitor the database tables. Let's instruct Django to run any migrations. Typically, we don't want to do that every time we fire up the container, so I just use a manual approach

```
docker-compose exec django_app python manage.py migrate
```

## Summary

In this post, I described how to containerize  a minimal Django-based web application that uses MySQL as a persistent layer.
Containers allow us to smooth development and testing of an application as they allow us to wrap the application alongside its dependencies.

However, managing many containers can be difficult. In this case using a container orchestration framework such as <a href="https://kubernetes.io/">Kubernetes</a>
may be useful.

## References

1. <a href="https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application">Dockerizing a Python Django Web Application</a>
2. <a href="https://realpython.com/django-development-with-docker-compose-and-machine/">Django Development with Docker Compose and Machine</a>
3. <a href="https://nickjanetakis.com/blog/dockerize-a-flask-celery-and-redis-application-with-docker-compose">Dockerize a Flask, Celery, and Redis Application with Docker Compose</a>
4. <a href="https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/">Dockerizing Django with Postgres, Gunicorn, and Nginx</a>
