from pathlib import Path
import importlib
import cherrypy
from quickweb.cli.colorhelper import info


def activate():
    boot_dir = Path("boot")
    boot_scripts = Path(boot_dir).glob("*.py")
    for boot_filename in boot_scripts:
        boot_name = boot_filename.stem
        print(f"** Running boot script {info(boot_filename)}")
        spec = importlib.util.spec_from_file_location(
            "boot_" + boot_name, boot_filename
        )
        boot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(boot_module)
        boot_module.start()
        cherrypy.engine.autoreload.files.add(boot_filename.as_posix())
    cherrypy.engine.autoreload.files.add(boot_dir.as_posix())
