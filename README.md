# biojs-backend
Backend repository for [biojs.io](biojs.io) website.

## Overview

This repository contains the source code for the backend of [biojs.io](biojs.io) website, maintained by the BioJS organization.
It uses the [Django](https://www.djangoproject.com/) Framework. It is in its dormant stage right now. This README will be updated along with the progress made. A detailed report can be found on the [BioJS Blog](http://biojs.net/).

## Setup

``` bash
# install pip
$ sudo apt-get install python-pip   # For Ubuntu
$ sudo easy_install pip             # For OSX

# install virtualenv
$ pip install virtualenv

# create a directory at the desired location for the virtual environment and create the environment
$ mkdir venv && cd venv
$ virtualenv .
$ source bin/activate               # Activate the virtual environment

# clone the repository at the location of your choice and install the dependencies
$ git clone https://github.com/biojs/biojs-backend.git
$ cd biojs-backend
$ pip install -r requirements.txt

# migrate the database
$ python manage.py migrate

# Create a personal Github access token in settings and use github username for CLIENT_ID
# export Github credentials to bypass rate limit
$ export GITHUB_CLIENT_ID=<username> && export GITHUB_CLIENT_SECRET=<token>

# start the server
$ python manage.py runserver

# Collect components
$ python manage.py updatecomponents
```

Navigate to [127.0.0.1:8000](http://127.0.0.1:8000/).

## Settings

### Debugging

Enable debug logs by editing the DEBUG=False setting in `biojs/settings.py`
