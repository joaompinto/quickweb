# -*- coding: utf-8 -*-
"""
    This module provides the web engine core startup/application configuration logic
"""
import os
import sys
from os.path import abspath, join, dirname

import cherrypy
import quickweb
from quickweb import controller, data_provider
from quickweb.colorhelper import info, print_error, print_warn

web_app_config = {}


def setup_app(app_name, app_directory, no_logs):
    """ setup the application initial configuration """

    test_mode = os.getenv("TEST_MODE")
    if test_mode:
        print_warn('Running in TEST mode')

    app_directory = abspath(app_directory)

    os.chdir(app_directory)
    set_engine_config(test_mode, no_logs)
    setup_features()

    data_provider.set_base_dir(app_directory)
    cherrypy.tree.mount(controller.get_app_root(), config=web_app_config)


def setup_features():
    """ Call the features setup function """

    core_features = {
        'web': [
            'content_directory',
            'controllers',
            'templates'
            ]
        }

    imported_features = []
    for feature_type, feature_list in core_features.items():
        features_list_names = ', ' .join(feature_list)
        print("** Setting up {0} features {1}"
              .format(info(feature_type), info(features_list_names)))
        for feature_name in feature_list:
            script_dir = dirname(abspath(__file__))
            module_fname = join(script_dir, 'features', feature_type, feature_name+".py")

            feature_dict = {}
            with open(module_fname) as source_file:
                exec(compile(source_file.read(), module_fname, 'exec'), feature_dict)
            try:
                feature = feature_dict['Feature']()
            except KeyError:
                print_error("Feature module '%s' does not provide a Feature class!" % feature_name)
                sys.exit(1)
            try:
                feature.setup()
            except:  # NOQA: E722
                print_error("Failed setting up feature '%s' !" % feature_name)
                raise
            imported_features.append(feature)

        for feature in imported_features:
            if hasattr(feature, "activate"):
                feature.activate()


def set_engine_config(test_mode, no_logs):
    """ Set engine global config options """
    quickweb.is_production = os.getenv('QUICKWEB_PRODUCTION', False)

    # Enforce utf8 encoding
    app_config = {
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8', 'tools.encode.errors': 'replace',
        'tools.trailing_slash.on': False,
        'tools.sessions.on': True,
        'checker.on': False
    }

    if test_mode:
        app_config.update(
            {
                'log.screen': False,
                'log.access_file': "access.log",
                'log.error_file': "error.log",
                'engine.autoreload.on': True
            }
        )
    # Disable logging when running with --no-logs
    if no_logs:
        app_config.update(
            {
                'log.screen': False,
                'log.access_file': None,
                'log.error_file': None,
            }
        )

    cherrypy.config.update(app_config)
