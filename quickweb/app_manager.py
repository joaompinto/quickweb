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
import quickweb.app
from quickweb.colorhelper import info, warning, success, print_error, print_success
from quickweb.template_manager import download_template
from quickweb import controller, doc


def create(app_directory, template_name, force):
    """
    Create an application using a template
    """
    print("** Creating app on directory %s " % (info(app_directory + "/")))

    if exists(app_directory):
        if force:
            shutil.rmtree(app_directory)
        else:
            print_error(app_directory + " already exists!")
            print("Use %s if you want to overwrite." % warning("--force"))
            sys.exit(2)

    download_template(template_name, app_directory)
    doc_path = os.path.dirname(doc.__file__)
    quickweb_required_mask = join(doc_path, "*.md")
    required_files = glob(quickweb_required_mask)
    base_required_files = [basename(x) for x in required_files]
    print(
        "** Adding startup files %s from %s"
        % (info(str(base_required_files)), info(doc_path))
    )
    for filename in required_files:
        shutil.copy(filename, app_directory)
    print_success("Application successfully created.")
    print_success("You can start it with:")
    print("    " + success("quickweb run " + app_directory))
    print_success("Or read about the app structure with:")
    print("    " + success("more " + join(app_directory, "QuickWeb_Application.md")))
    print("**")


def run(app_directory, listener_address, no_logs):
    quickweb.app.run(app_directory, listener_address, no_logs)


def describe(app_directory):
    quickweb.app.run(app_directory, running_describe=True)
    for key, values in controller._app_root.__dict__.items():
        print(key, values)


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
