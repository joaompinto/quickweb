# -*- coding: utf-8 -*-
import os
import re
import sys
import cherrypy
import importlib
from os.path import join, exists, basename, splitext
from glob import glob

this = sys.modules[__name__]


class ApplicationNode:
    pass


this._app_root = ApplicationNode()
this._template_engine = None

# Dictionary with URL to Name mapping to be displayed on navigation components
this._navigation = {}

# List of "place_after" constraints
this._navigation_place_after = []


def set_app_root(controller_obj):
    for key, value in this._app_root.__dict__.items():
        setattr(controller_obj, key, value)
    this._app_root = controller_obj


def get_app_root():
    return this._app_root


def find_path_base(controller_path_name):
    controller_path_name = controller_path_name.strip(os.sep)
    path_parts = controller_path_name.split(os.sep)

    path_root = this._app_root

    path_to_resource = path_parts[:-1]
    for part_name in path_to_resource:
        new_path_root = getattr(path_root, part_name, None)
        path_root = new_path_root
    return path_root


def attach(controller_path_name, controller_obj):
    """ Binds a controller object to an application URL """

    # Map OS path separator to URL separators (Needed on Windows)
    controller_path_name = controller_path_name.replace(os.sep, "/")

    controller_path_name = controller_path_name.strip("/")
    path_parts = controller_path_name.split("/")

    #  print('attach', controller_path_name, controller_obj, len(this.app_root.__dict__))
    path_root = this._app_root

    # If a path
    resource_name = path_parts[-1]
    path_to_resource = path_parts[:-1]
    for part_name in path_to_resource:
        new_path_root = getattr(path_root, part_name, None)
        if new_path_root is None:
            new_path_root = ApplicationNode()
            setattr(path_root, part_name, new_path_root)
        path_root = new_path_root

    # If we get a new root index, migrate current root resources to the new one
    if controller_path_name == "":
        set_app_root(controller_obj)
    else:
        setattr(path_root, resource_name, controller_obj)


def publish(func=None, *args):
    return cherrypy.expose(func, *args)


def redirect(url):
    raise cherrypy.HTTPRedirect(url)


def get_cookie(name, default_value=None):
    def unescape(s):
        m = re.match(r'^"(.*)"$', s)
        s = m.group(1) if m else s
        return s.replace("\\\\", "\\")

    if name in cherrypy.request.cookie:
        return unescape(cherrypy.request.cookie[name].value).decode("unicode-escape")
    else:
        return default_value


def get_session_value(name, default_value=None):
    if name in cherrypy.session:
        return cherrypy.session[name]
    else:
        return default_value


def set_session_value(name, value):
    cherrypy.session[name] = value


def set_cookie(name, value, path="/", max_age=3600, version=1):
    cookie = cherrypy.response.cookie
    cookie[name] = value.encode("unicode-escape")
    cookie[name]["path"] = path
    cookie[name]["max-age"] = max_age
    cookie[name]["version"] = version


def delete_cookie(name):
    cherrypy.response.cookie[name] = "deleting"
    cherrypy.response.cookie[name]["expires"] = 0


def set_response(name, value):
    cherrypy.response.headers[name] = value


def method():
    return cherrypy.request.method


def params():
    return cherrypy.request.params


def controller_url():
    """
    @return: the current request url
    """
    return cherrypy.request.path_info


def controller_path():
    """
    @return: the current request path
    """
    return cherrypy.request.path_info.split("/")


def get_config():
    return cherrypy.config


def navigation_elements(start_path=None, using_placement=True):
    """
    Returns a list with { 'name': name, 'link': link}
    for each renderable ellement found on path
    """
    app_node = get_app_root()
    _navigation = app_node.__dict__.get("_navigation")
    if _navigation:
        return _navigation

    nav_list = []
    for leaf_name, leaf_obj in get_app_root().__dict__.iteritems():
        contains_index = hasattr(leaf_obj, "index")
        if contains_index and leaf_name[0] != "_":
            nav_name = this._navigation.get(leaf_name, leaf_name)
            nav_list.append({"name": nav_name, "link": leaf_name})

    if using_placement:
        for constraint_source, constraint_target in this._navigation_place_after:
            source_pos = [
                i for i, x in enumerate(nav_list) if x["link"] == constraint_source
            ][0]
            target_pos = [
                i for i, x in enumerate(nav_list) if x["link"] == constraint_target
            ][0]
            if source_pos < target_pos:
                swapping_element = nav_list.pop(source_pos)
                nav_list.insert(target_pos, swapping_element)

    return nav_list


def current_path():
    return controller_path()[1]


def helpers():
    """ Returns a dict with objects that should be available to templates """
    helpers_dict = {
        "navigation_elements": navigation_elements,
        "current_path": current_path,
        "language": get_lang,
        "domain": get_domain,
        "scheme": get_scheme,
        "session": get_session_value,
    }
    return helpers_dict


def get_host():
    for key, value in cherrypy.request.header_list:
        if key.upper() == "HOST":
            return value.lower()


def get_lang():
    lang = "en"
    host = get_host()
    if host and "." in host:
        lang = host.split(".")[0]
    return lang


def get_domain():
    host = get_host()

    if host:
        if "." in host:
            domain = ".".join(host.split(".")[1:])
        else:
            domain = host
        return domain


def get_scheme():
    if os.environ.get("FORCE_HTTPS"):
        return "https"
    return cherrypy.request.scheme


def set_navigation_info(*args, **kwargs):
    #  cherrypy.(str(args))
    #  cherrypy.log(str(kwargs))

    cherrypy.log("Setting navigation info %s %s" % (str(args), str(kwargs)))

    valid_kwargs = ["name", "place_after"]
    for k in kwargs:
        if k not in valid_kwargs:
            raise Exception("Unsupported parameter %s" % k)

    if "name" in kwargs:
        this._navigation[current_path()] = kwargs["name"]

    # While the code provides support for multiple types, for simplicity only 'place_after'
    # is implemented.
    constraint_target = kwargs.get("place_after")
    if constraint_target[0] != "/":
        constraint_target = "/" + constraint_target

    if not constraint_target:
        return

    was_found = [
        x
        for x in navigation_elements(using_placement=False)
        if x["link"] == constraint_target
    ]

    if not was_found:
        cherrypy.log("Unknown target " + constraint_target)
        return

    was_found = [x for x in this._navigation_place_after if x[2] == constraint_target]

    if was_found:
        raise Exception("Duplicated place_after for target '%s'" % constraint_target)

    this._navigation_place_after((current_path(), constraint_target))


def load_app_modules(app_directory):
    libglob = join(app_directory, "lib", "*.py")
    libinit_fname = join(app_directory, "lib", "__init__.py")
    if not exists(libinit_fname):
        return

    spec = importlib.util.spec_from_file_location("lib", libinit_fname)
    lib_load_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib_load_module)
    setattr(this, "lib", lib_load_module)

    libdir = join(app_directory, "lib")
    sys.path.append(libdir)

    for filename in glob(libglob):
        print("** Loading library", filename)
        module_name = splitext(basename(filename))[0]
        spec = importlib.util.spec_from_file_location(module_name, filename)
        load_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(load_module)
        setattr(lib_load_module, module_name, load_module)
        cherrypy.engine.autoreload.files.add(filename)

    sys.path.remove(libdir)


def render(name, lang=None, **kwargs):
    if not lang:
        lang = get_lang()
    return this._template_engine.render(name, lang, **kwargs)
