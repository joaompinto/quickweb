#! /usr/bin/env python

"""QuickWeb

Usage:
    quickweb create <app_directory> <template_name> [--force]
    quickweb run [<app_directory>] [-l <listener_address>] [--no-logs]
    quickweb setup-cf-deployment [<app_directory>]
    quickweb setup-docker-deployment [<app_directory>]
    quickweb describe [<app_directory>]
    quickweb templates

Examples:

    quickweb create my-quickweb-app bootstrap-navbar-fixed-top

Options:
  -h --help     Show this screen.
"""
import os
import sys
from os.path import join, dirname
from docopt import docopt
from colorama import init
from quickweb import app_manager, template_manager, version


init()

# Make sure we use the source directory for imports when running during development
script_dir = join(dirname(os.path.realpath(__file__)), "..")
sys.path.insert(0, script_dir)


def main():
    arguments = docopt(__doc__, version="QuickWeb %s" % version.version)
    print()

    if arguments["create"]:
        app_manager.create(
            arguments["<app_directory>"],
            arguments["<template_name>"],
            arguments["--force"],
        )

    if arguments["run"]:
        app_manager.run(
            arguments["<app_directory>"],
            arguments["<listener_address>"],
            arguments["--no-logs"],
        )

    if arguments["setup-cf-deployment"]:
        app_manager.setup_cf_deployment(arguments["<app_directory>"])

    if arguments["setup-docker-deployment"]:
        app_manager.setup_docker_deployment(arguments["<app_directory>"])

    if arguments["describe"]:
        app_manager.describe(arguments["<app_directory>"])

    if arguments["templates"]:
        template_manager.list()


if __name__ == "__main__":
    main()
