#! /usr/bin/env python

"""QuickWeb

Usage:
    quickweb create <app_directory> <template_name> [--force]
    quickweb run [<app_directory>] [-l <listener_address>] [--no-logs]
    quickweb setup-cf-deployment [<app_directory>]
    quickweb setup-docker-deployment [<app_directory>]
    quickweb templates

Examples:

    quickweb create my-quickweb-app bootstrap-navbar-fixed-top

Options:
  -h --help     Show this screen.
"""
import os
import sys
import colorama
from os.path import join, dirname
from .app_manager.create import CreateCommand
from cleo import Application

colorama.init()  # Required to init terminal emulation on Windows

# Make sure we use the source directory for imports when running during development
script_dir = join(dirname(os.path.realpath(__file__)), "..")
sys.path.insert(0, script_dir)


application = Application()
application.add(CreateCommand())

if __name__ == "__main__":
    application.run()
