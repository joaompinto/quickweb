#!/usr/bin/python
""" core engine package """

import os.path
import cherrypy


def version():
    """ Return quickweb engine version """

    quickweb_dir = os.path.dirname((os.path.realpath(__file__)))
    version_filename = os.path.join(quickweb_dir, "version")
    with open(version_filename) as version_file:
        on_file_version = version_file.readline().strip("\r\n")

    return on_file_version


log = cherrypy.log  # noqa: E305
