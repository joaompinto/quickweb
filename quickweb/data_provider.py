# -*- coding: utf-8 -*-
"""
    This module provides the local data providers.
    It can be used from both templates and controllers to
    for data fetching.
"""
import os
import sys
import json
from urllib.parse import urlparse
from os.path import abspath, splitext, isfile, join
import cherrypy
import yaml

this = sys.modules[__name__]

this.data_path = None
this.psycopg2_available = True

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    this.psycopg2_available = False


# this is a pointer to the module object instance itself.


def get_postgresql(provider_url):
    """ retrievede data from table matching the 'provider_url' """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:  # There is no DB configured
        return None

    if not this.psycopg2_available:
        raise Exception(
            "You must install the psycopg2 python package to use a database."
        )

    conn = psycopg2.connect(database_url)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT * FROM %s;" % provider_url)
    except psycopg2.ProgrammingError as e:
        if e.pgcode == "42P01":  # UNDEFINED TABLE
            conn.close()
            return None
    resultset = cur.fetchall()
    data = []
    for row in resultset:
        data.append(row)
    cur.close()
    conn.close()
    return data


def _search_path(provider_name):
    parsed_url = urlparse(provider_name)
    if parsed_url.scheme != "":  # Schemes are note supported at this time
        return
    if parsed_url.path.startswith("/"):  # Absolute paths are not allowed
        return
    resource_path = abspath(join(this.data_path, parsed_url.path))
    filename, file_extension = splitext(resource_path)
    if file_extension == "":  # Attempt with all supported file type extentions
        search_path = []
        for extension in [".yaml", ".json"]:
            search_path.append(resource_path + extension)
    else:
        search_path = [resource_path]


def get(provider_name, provider_key=None):
    """ Return an iterable object with data content.
    """
    search_path = _search_path(provider_name)

    found_resource_path = None
    for path in search_path:
        if isfile(path):
            found_resource_path = path
            break

    # First attemtp to find a local provider, if not found, try the database
    if not found_resource_path:
        data = get_postgresql(provider_name)
        if data is None:
            raise cherrypy.HTTPError(
                404, "Unable to locate data provider for '%s'" % provider_name
            )

    filename, file_extension = splitext(found_resource_path)
    if file_extension == ".yaml":
        data = load_yaml(found_resource_path)
    if file_extension == ".json":
        data = json.load(found_resource_path)

    if provider_key:
        return data[provider_key]
    else:
        return data


def load_yaml(filename):
    multi_document_found = False
    with open(filename) as data_file:
        try:
            data = yaml.safe_load(data_file)
        except yaml.composer.ComposerError:
            multi_document_found = True
    if multi_document_found:
        with open(filename) as data_file:
            data = [x for x in yaml.safe_load_all(data_file) if x]
    return data


def set_base_dir(data_path):
    this.data_path = data_path


def data_title(provider_name):
    """ because this is a very frequently used item fetch """
    return get(provider_name, "title")
