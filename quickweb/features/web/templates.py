#!/usr/bin/python
""" Provides dynamic content using a template engine """

import yaml
import re
import cherrypy

from os import environ
from os.path import basename, dirname, join, exists, getmtime, splitext, sep
from jinja2 import TemplateNotFound, Environment, select_autoescape, meta
from jinja2 import BaseLoader, Markup, escape
from markdown import markdown
from importlib.machinery import SourceFileLoader

from quickweb import controller
from quickweb.events import on_event
from quickweb.modules import fnmatch_list


class Feature(object):
    """ templates """

    _template_engine = None

    def setup(self):
        """ config contains a list of config sections """
        on_event("content_directory_set", self.on_content_directory_set)
        on_event("content_file_found", lambda x, y: self.on_found_content_file(x, y))

    def on_content_directory_set(self, content_directory):
        self._template_engine = TemplateEngine(content_directory)
        controller._template_engine = self._template_engine

    def on_found_content_file(self, content_root, content_name):
        """ A file was found """
        on_file_name = ["*.html", "*.md"]
        file_exclude = "_*"

        # We only care if it matches our selection pattern
        if not fnmatch_list(basename(content_name), on_file_name):
            return

        if file_exclude and fnmatch_list(basename(content_name), file_exclude):
            return

        # There is a py file associated with the content file, load it
        py_fn = splitext(content_root + sep + content_name)[0] + ".py"
        render_func = None
        if exists(py_fn):
            controller_module = SourceFileLoader(py_fn, py_fn).load_module()
            try:
                render_func = controller_module.render
            except AttributeError:
                raise
            cherrypy.engine.autoreload.files.add(py_fn)

        url = "/" + content_name
        noext_name, ext = splitext(url)
        url = noext_name

        # Map 'index' files to dirname/
        if basename(url) == "index":
            url = dirname(url)

        template_controller = TemplateController(
            content_name, self._template_engine, render_func
        )
        controller.attach(url, template_controller)


class TemplateController(object):
    """ Render templates from a webroot dir """

    def __init__(self, path, template_engine, render_func):
        self._path = path
        self._template_engine = template_engine
        self._render_func = render_func

    @controller.publish
    def index(self):
        kwargs = {}
        if self._render_func:
            kwargs = self._render_func()
        return self._template_engine.render(self._path, controller.get_lang(), **kwargs)


class TemplateEngine:
    """
    This classes provides a Jinja2 based template renderer, extended with the following:
        - Inject quickweb specific helper functions to be used on templates (e.g. current_path)
        - If there is a .yaml file matching the name, pass it's content as template variables
    """

    _engine = None
    _loader = None
    _template_base_path = None

    def __init__(self, template_base_path):
        self._template_base_path = template_base_path
        self._loader = QWTemplateLoader(template_base_path)
        self._engine = Environment(
            autoescape=select_autoescape(["html", "xml"]), loader=self._loader
        )
        self._engine.globals.update(controller.helpers())
        self._engine.filters["paragraphs"] = paragraphs
        self._engine.filters["markdown"] = lambda x: Markup(markdown(x))
        self._engine.filters["environ"] = env_override

    def render(self, name, lang, **kwargs):

        template = self._engine.get_template(name)
        # Load .yaml data for all referenced templates
        referenced_templates = self._loader.referenced_templates(name)
        # Load .yaml data for the requested template
        referenced_templates.append(name)
        yaml_variables = {}
        for template_name in referenced_templates:
            noext_name, ext = splitext(template_name)
            for try_part in [noext_name + "_" + lang, noext_name]:
                yaml_data_filename = try_part + ".yaml"
                try:
                    yaml_renderer = self._engine.get_template(yaml_data_filename)
                except TemplateNotFound:
                    pass
                else:
                    yaml_data = yaml.safe_load(yaml_renderer.render())
                    yaml_variables.update(dict(yaml_data))
                    break
        yaml_variables["env"] = environ
        yaml_variables.update(**kwargs)

        return template.render(**yaml_variables)


def env_override(value, key):
    return environ.get(key, value)


class QWTemplateLoader(BaseLoader):
    """
    The QWTemplateLoader loads plain Jinja2 templates from files, and augments them
    with the QuickWeb application specific behavior:
        - If the template does not start with a '_' and there is a '_base.html' file, change the
        memory loaded template source to be extended from '_base.html'
        - Identify other templates included/extended from the loded one, this list will be required
        during rendering, because the .yaml content bind to every included template must be
        provided.
    """

    _included_templates = {}  # List of templates included by a specific template

    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        template_fn, template_ext = splitext(template)
        path = join(self.path, template)
        if not exists(path):
            raise TemplateNotFound(template)
        mtime = getmtime(path)
        with open(path, "rb") as f:
            source = f.read().decode("utf-8")
        if template_ext == ".md":
            source = markdown(source, extensions=["markdown.extensions.attr_list"])
        # If the .html does not extend other template, check if there is _base.html .
        # We will extend the template file from _base.html if present.
        if (
            template_ext in [".html", ".md"]
            and not re.match(r'^\s*{% extends "', source)
            and not basename(template)[0] == "_"
        ):
            _base_filename = join(self.path, "_base.html")
            if exists(_base_filename):
                extended_source = '{% extends "_base.html" %}\n'
                extended_source += "{% block content %}"
                extended_source += source
                extended_source += "{% endblock %}"
                source = extended_source

        # Set dependencies for this template
        referenced_templates = self._find_referenced_templates(
            template, source, environment
        )
        self._included_templates[template] = referenced_templates

        return source, path, lambda: mtime == getmtime(path)

    def _find_referenced_templates(self, name, source, environment):
        try:
            ast = environment.parse(source)
        except:  # NOQA: E722
            print("Error rendering template " + name)
            raise
        references = [x for x in meta.find_referenced_templates(ast)]
        for name in references:
            with open(join(self.path, name), "rb") as f:
                source = f.read().decode("utf-8")
                references.extend(
                    self._find_referenced_templates(name, source, environment)
                )
        return references

    def referenced_templates(self, name):
        return self._included_templates.get(name)


def paragraphs(input):
    """ Split lines and return them enclosed in HTML paragraphs """
    html_p_list = list(
        map(lambda x: "<p>{0}</p>".format(escape(x)), input.splitlines())
    )
    return Markup("".join(html_p_list))


# In case jinja2 extenions become a need, some good examples can be found at:
#  https://github.com/ckan/ckan/blob/master/ckan/lib/
