import cherrypy
import importlib
import sys
from pathlib import Path
from quickweb.cli.colorhelper import info
import quickweb.app.modules


def activate():
    modules_dir = Path("modules")
    if not modules_dir.exists():
        return
    libinit_fname = Path("modules", "__init__.py")
    if not libinit_fname.exists():
        raise Exception("modules dir does not provide an __init__.py")

    spec = importlib.util.spec_from_file_location("lib", libinit_fname)
    lib_load_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib_load_module)
    setattr(quickweb.app.modules, "modules", lib_load_module)

    libdir = Path("modules")
    sys.path.append(libdir)

    module_list = Path("modules").glob("*.py")
    for filename in module_list:
        print("** Importing", info(filename))
        module_name = filename.stem
        spec = importlib.util.spec_from_file_location(module_name, filename)
        load_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(load_module)
        setattr(lib_load_module, module_name, load_module)
        cherrypy.engine.autoreload.files.add(filename.as_posix())

    sys.path.remove(libdir)
