# -*- coding: utf-8 -*-
from os.path import join, basename
from quickweb import controller, template
from glob import glob
from time import time
import imp
import cherrypy
import os
import logging.config
import warnings


# Set a default app root handler, to bind controllers until we find an
# "index" controller
class TemplateRenderer(object):  # Application Server Root place holder
    @controller.publish
    def index(self):
        path = controller.controller_path()[1]
        if path == "":
            html_template_filename = "index.html"
        else:
            html_template_filename = path + ".html"
        return template.render(html_template_filename)


def setup_logging():
    LOG_CONF = {
        "version": 1,
        "formatters": {
            "void": {"format": ""},
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "cherrypy_console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "void",
                "stream": "ext://sys.stdout",
            },
            "cherrypy_access": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "void",
                "filename": "access.log",
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8",
            },
            "cherrypy_error": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "void",
                "filename": "errors.log",
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "INFO"},
            "db": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "cherrypy.access": {
                "handlers": ["cherrypy_access"],
                "level": "INFO",
                "propagate": False,
            },
            "cherrypy.error": {
                "handlers": ["cherrypy_console", "cherrypy_error"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(LOG_CONF)


def set_default_config():

    # Enforce utf8 encoding
    cherrypy.config.update(
        {
            "tools.encode.on": True,
            "tools.encode.encoding": "utf-8",
            "tools.encode.errors": "replace",
        }
    )
    cherrypy.config.update({"tools.sessions.on": True})
    cherrypy.config.update({"environment": "embedded"})
    setup_logging()


# Load and setup controllers
def load_controllers(app_name, controller_dir):
    print("*** Checking for controllers")
    for controller_file in glob(join(controller_dir, "*.py")):
        module_name = app_name + ".controllers." + basename(controller_file)
        controller_path = basename(controller_file).split(".")[0]
        print("- Loading controller %s -> %s " % (module_name, controller_path))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            handler = imp.load_source(module_name, controller_file)
        controller.attach(controller_path, handler.Controller())


def set_template_dirs(template_dirs, webroot_directory):
    for template_dirname in template_dirs:
        print("- Setting template directory", template_dirname)
    template.set_directories(webroot_directory, template_dirs)


def set_root_appnodes(webroot_directory):
    for html_filename in glob(join(webroot_directory, "*.html")):
        node_name = html_filename.split("/")[-1].split(".")[0]
        if node_name.startswith("_"):  # Dot not render template elements
            continue
        if node_name == "index":  # Index is already handled by the root dir
            continue
        controller.attach("/" + node_name, TemplateRenderer())


# Setup static file serve handling for 'static' sub-dirs
def set_static_dirs(application, static_dirs):
    print("*** Checking for static dirs")
    for location in static_dirs:
        for static_dir in os.listdir(location):
            full_static_dir = join(location, static_dir)
            print("- Setting static dir %s -> %s" % (static_dir, full_static_dir))
            conf = {}
            conf["/" + basename(static_dir)] = {
                "tools.staticdir.dir": full_static_dir,
                "tools.staticdir.on": True,
            }
            application.merge(conf)


def setup(app_name, app_directory):

    quickweb_dir = os.path.dirname((os.path.realpath(__file__)))
    version_filename = os.path.join(quickweb_dir, "..", "version")
    with open(version_filename) as version_file:
        version = version_file.readline().strip("\r\n")

    application_root = controller.set_approot(TemplateRenderer())
    app = cherrypy.Application(application_root, script_name=None, config=None)

    set_default_config()

    start_t = time()
    print(
        "=" * 10
        + " Starting app %s using QuickWeb %s " % (app_name, version)
        + "=" * 10
    )
    print("= Startup location", app_directory)
    static_dirs = []
    webroot_directory = join(app_directory, "webroot")
    for location in ["template", "webroot"]:
        for root, dirs, files in os.walk(join(app_directory), location):
            for name in dirs:
                if name == "static":
                    static_directory = join(join(root, name))
                    if static_directory not in static_dirs:
                        static_dirs.append(static_directory)

    set_static_dirs(app, static_dirs)
    set_root_appnodes(webroot_directory)
    load_controllers(app_name, join(app_directory, "controllers"))
    stop_t = time()
    print("=" * 10 + " Startup completed in %0.3f ms " % ((stop_t - start_t) * 1000.0))

    return app
