# -*- coding: utf-8 -*-
"""
    This module provides the web engine core startup/application configuration logic
"""
import os
import importlib
from glob import glob

import cherrypy
import quickweb
from quickweb.server import controller
from quickweb.cli.colorhelper import print_warn
from . import web, modules, boot

web_app_config = {}


def activate(app_directory):
    """ setup the application initial configuration """

    os.chdir(app_directory)
    modules.activate()
    boot.activate()
    # tools.activate()
    web.activate()

    test_mode = os.getenv("TEST_MODE")
    if test_mode:
        print_warn("Running in TEST mode")

    # app_directory = abspath(app_directory)
    # controller.load_app_modules(app_directory)

    # run_boot(app_directory)
    # set_engine_config(test_mode, no_logs)
    # load_tools(app_directory)

    # data_provider.set_base_dir(app_directory)


def load_tools(app_directory):
    tools_dir = join(app_directory, "tools")
    tools_glob = join(tools_dir, "*.py")
    for tool_filename in glob(tools_glob):
        tool_name = basename(tool_filename).split(".")[0]
        print(f"** Loading tool {tool_filename}")
        spec = importlib.util.spec_from_file_location(
            "tools_" + tool_name, tool_filename
        )
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        app_config = {f"tools.{tool_name}.on": True}
        cherrypy.config.update(app_config)
        cherrypy.engine.autoreload.files.add(tool_filename)
    cherrypy.engine.autoreload.files.add(tools_dir)


def set_engine_config(test_mode, no_logs):
    """ Set engine global config options """
    quickweb.is_production = os.getenv("QUICKWEB_PRODUCTION", False)

    # Enforce utf8 encoding
    app_config = {
        "tools.encode.on": True,
        "tools.encode.encoding": "utf-8",
        "tools.encode.errors": "replace",
        "tools.trailing_slash.on": False,
        "checker.on": False,
    }

    if test_mode:
        app_config.update(
            {
                "log.screen": False,
                "log.access_file": "access.log",
                "log.error_file": "error.log",
                "engine.autoreload.on": True,
            }
        )

    # Disable logging when running with --no-logs
    if no_logs:
        app_config.update(
            {"log.screen": False, "log.access_file": None, "log.error_file": None}
        )

    cherrypy.config.update(app_config)
