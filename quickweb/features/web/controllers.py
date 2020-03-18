#!/usr/bin/python
""" Provides dynamic content using python controller """
from os.path import basename, join, splitext
from fnmatch import fnmatch
import imp
import warnings
import cherrypy

from quickweb import controller
from quickweb.events import on_event


class Feature(object):
    """ templates """

    def setup(self):
        on_event("content_file_found", lambda x, y: self.on_found_content_file(x, y))

    def on_found_content_file(self, content_root, content_name):
        """ A file was found """
        on_file_name = "*.py"

        # We only care if it matches our selection pattern
        if not fnmatch(basename(content_name), on_file_name):
            return

        url = "/" + content_name

        noext_name, ext = splitext(url)
        url = noext_name

        module_fname = join(content_root, content_name)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            controller_module = imp.load_source(module_fname, module_fname)
        controller.attach(url, controller_module.Controller())
        cherrypy.engine.autoreload.files.add(module_fname)
