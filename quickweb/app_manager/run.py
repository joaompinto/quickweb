"""
"""
import os
from time import time
import cherrypy
import quickweb
import quickweb.app_dir
from quickweb.cli.colorhelper import info
from cheroot.server import HTTPServer
from cheroot.ssl.builtin import BuiltinSSLAdapter
from cherrypy.process.plugins import Daemonizer, PIDFile
import ssl
from .. import app_dir


def run(app_directory, listener_address=None):
    """
    """
    start_t = time()  # Used for startup time calculation
    print("** Starting QuickWeb %s" % info(quickweb.version.version))
    print("** Starting application from directory %s" % info(app_directory))
    startup_cwd = os.getcwd()

    # Identify the application root directory
    app_root_directory = app_directory or os.getcwd()
    app_dir.activate(app_root_directory)

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

    ssl_certificate = os.environ.get("SSL_CERTIFICATE")
    if ssl_certificate:
        ssl_adapter = BuiltinSSLAdapter(
            certificate=ssl_certificate,
            private_key=os.environ["SSL_PRIVATE_KEY"],
            certificate_chain=os.environ.get("SSL_CERTIFICATE_CHAIN"),
        )
        verify_mode = ssl.CERT_NONE
        if os.getenv("SSL_VERIFY_CLIENT_CERT") == "required":
            verify_mode = ssl.CERT_REQUIRED
        if os.getenv("SSL_VERIFY_CLIENT_CERT") == "optional":
            verify_mode = ssl.CERT_OPTIONAL
        ssl_adapter.context.verify_mode = verify_mode
        HTTPServer.ssl_adapter = ssl_adapter

    # In some platforms signals are not available:
    if hasattr(cherrypy.engine, "signals"):
        cherrypy.engine.signals.subscribe()
    cherrypy.engine.subscribe("stop", lambda: os.chdir(startup_cwd))
    if os.environ.get("DAEMON_MODE"):
        daemon = Daemonizer(cherrypy.engine, stdout="stdout.log", stderr="stderr.log")
        daemon.subscribe()
    PIDFile(cherrypy.engine, "quickweb.pid").subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
