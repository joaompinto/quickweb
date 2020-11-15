#!/usr/bin/python
"""
This module implements the application management commands
"""
import shutil
import sys
import os
from glob import glob
from os.path import basename, exists, join, isdir

import quickweb
from quickweb.cli.colorhelper import info, warning, success, print_error, print_success
from quickweb.template_manager import download_template
from quickweb.server import controller


def setup_cf_deployment(app_directory):
    app_directory = app_directory or os.getcwd()
    app_name = basename(app_directory)
    webroot_dir = join(app_directory, "webroot")
    if not isdir(webroot_dir):
        print_error("Unable to find webroot directory '%s'" % webroot_dir)
        exit(2)

    manifest_yaml = """\
---
applications:
- name: {0}
  memory: 128M
  buildpack: python_buildpack
  random-route: true # Choose a proper hostname with host: name
""".format(
        app_name
    )
    with open(join(app_directory, "manifest.yaml"), "w") as manifest_file:
        manifest_file.write(manifest_yaml)
    with open(join(app_directory, "requirements.txt"), "w") as requests_file:
        requests_file.write("quickweb>={0}\n".format(quickweb.version()))

    with open(join(app_directory, "Procfile"), "w") as procfile:
        procfile.write("web: quickweb run . --no-logs\n")


def setup_docker_deployment(app_directory):
    app_directory = app_directory or os.getcwd()
    webroot_dir = join(app_directory, "webroot")
    if not isdir(webroot_dir):
        print_error("Unable to find webroot directory '%s'" % webroot_dir)
        exit(2)

    dockerfile_txt = """\
FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "quickweb", "run", "/usr/src/app", "--no-logs" ]
"""
    with open(join(app_directory, "Dockerfile"), "w") as manifest_file:
        manifest_file.write(dockerfile_txt)
    with open(join(app_directory, "requirements.txt"), "w") as requests_file:
        requests_file.write("quickweb>={0}\n".format(quickweb.version()))
