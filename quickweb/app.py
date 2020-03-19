"""
"""
import os
import sys
from time import time
from os.path import join, exists
from glob import glob
import cherrypy
import quickweb
from quickweb import startup
from quickweb.colorhelper import info
import importlib


def run(app_directory, listener_address=None, no_logs=False, running_describe=False):
    """
    When an application is run, the following is performed:

    - Identify application root
        - Check for qwstart.py on
            - Startup script directory
            - Current working directory

    - Setup port number, if $PORT is not set, use a random port
    """
    start_t = time()  # Use for startup time calculation
    print(
        "** Starting application %s using QuickWeb %s "
        % (info(app_directory), info(quickweb.version()))
    )
    startup_cwd = os.getcwd()

    # Check if beeing run from gunicorn
    is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
    if is_gunicorn:
        sys.stderr.write(
            "Quickweb provides it's own HTTP server module.\n"
            "Running from another HTTP server is not supported at this time\n"
        )
        sys.exit(1)

    # Identify the application root directory
    app_root_directory = app_directory or os.getcwd()

    dbsupport_fname = join(app_root_directory, "dbsupport.py")
    dbsupport = None
    if exists(dbsupport_fname):
        spec = importlib.util.spec_from_file_location("dbsupport", dbsupport_fname)
        dbsupport = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dbsupport)

    startup.setup_app("app_name", app_root_directory, no_logs)

    if running_describe:
        return

    colored_elapsed_time = info("%0.2fms" % ((time() - start_t) * 1000.0))
    print("=" * 10 + " Startup completed in " + colored_elapsed_time)

    # Determine the HTTP listener port
    listener_port = int(os.getenv("PORT", 8080))
    if os.name == "posix":
        socket_host = "0.0.0.0"
    else:
        socket_host = "127.0.0.1"
    if listener_address is not None:
        socket_host = listener_address
    cherrypy.config.update({"server.socket_host": socket_host})
    cherrypy.config.update({"server.socket_port": listener_port})

    # In some platforms signals are not available:
    if hasattr(cherrypy.engine, "signals"):
        cherrypy.engine.signals.subscribe()
    cherrypy.engine.subscribe("stop", lambda: os.chdir(startup_cwd))
    if dbsupport:
        print("** Setting up datbase")
        cherrypy.engine.subscribe("start", dbsupport.setup_database)
        cherrypy.engine.subscribe("stop", dbsupport.cleanup_database)

    cherrypy.engine.start()
    cherrypy.engine.block()
