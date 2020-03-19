#!/usr/bin/python
""" Changes web content lookup directory """
import os
import sys
from os.path import isdir, join, exists, abspath
import cherrypy

from quickweb.colorhelper import print_error
from quickweb.events import invoke
from quickweb.startup import web_app_config


class Feature(object):
    """ content_directory """

    _content_directory = ""
    _static_directories = []

    def setup(self):
        """
        chdir() into the provided directory
        """
        content_directory = self._content_directory = "webroot"
        lib_directory = "lib"

        if not isdir(content_directory):
            print_error("Unable to find content directory '%s'" % content_directory)
            sys.exit(1)
        cherrypy.engine.autoreload.files.add(content_directory)
        cherrypy.engine.autoreload.files.add(lib_directory)

    def activate(self):
        """ Trigger the content dir/file_dir events """
        content_dir_len = len(self._content_directory)

        invoke("content_directory_set", self._content_directory)

        for root, dirs, files in os.walk(self._content_directory):
            for dir_name in dirs:
                relative_name = join(root, dir_name)[content_dir_len + 1 :]
                static_file_flag = join(root, dir_name, ".static")
                if exists(static_file_flag):
                    self.setup_static_dir(relative_name)
                else:
                    invoke("content_dir_found", self._content_directory, relative_name)
            for file_name in files:
                relative_name = join(root, file_name)[content_dir_len + 1 :]
                if not self.is_on_static_path(relative_name):
                    invoke("content_file_found", self._content_directory, relative_name)

    def setup_static_dir(self, content_name):
        """ A directory matched our dir specification """

        content_root = self._content_directory

        if self.is_on_static_path(content_name):
            return

        url = "/" + content_name
        # gerenate a static directory section for the cherrypy static dir tool
        static_conf = {
            url: {
                "tools.staticdir.dir": abspath(join(content_root, content_name)),
                "tools.staticdir.on": True,
                "tools.staticdir.content_types": {"svg": "image/svg+xml"},
            }
        }
        web_app_config.update(static_conf)

        self._static_directories.append(content_name)

    def is_on_static_path(self, content_name):
        for static_dir in self._static_directories:
            if content_name.startswith(static_dir):
                return True
        return False
