#!/usr/bin/python
""" Provides dynamic content using python controller """
from os.path import basename, join, splitext, dirname, exists, sep
from fnmatch import fnmatch
from importlib.machinery import SourceFileLoader
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

        # Ignore if there is a matching .html because it's a composed controller
        html_fn = splitext(content_root + sep + content_name)[0] + ".html"
        if exists(html_fn):
            return

        if basename(content_name) == "index.py":
            url = "/" + dirname(content_name)
        else:
            url = "/" + content_name
        noext_name, ext = splitext(url)
        url = noext_name

        module_fname = join(content_root, content_name)
        controller_module = SourceFileLoader(module_fname, module_fname).load_module()
        controller.attach(url, controller_module.Controller())
        cherrypy.engine.autoreload.files.add(module_fname)
