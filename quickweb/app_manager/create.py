import shutil
import quickweb.doc
from quickweb.cli.colorhelper import info, print_success, print_error, success, warning
from pathlib import Path
from ..template_manager import download_template
from cleo import Command


class CreateCommand(Command):
    """
    Create an application using a template

    create
        {app-directory : path to the directory containing the application}
        {template-name : name of the template to use}
        {--force : Force to overwrite <app-direcoty> if it already exists}
        """

    def handle(self):
        app_directory = self.argument("app-directory")
        template_name = self.argument("template-name")
        force = self.option("force")
        self.create(app_directory, template_name, force)

    def create(self, app_directory, template_name, force):
        """
        Create an application using a template
        """
        print("** Creating app on directory %s " % (info(app_directory + "/")))

        if Path(app_directory).exists():
            if force:
                shutil.rmtree(app_directory)
            else:
                print_error(app_directory + " already exists!")
                print("Use %s if you want to overwrite." % warning("--force"))
                exit(2)

        download_template(template_name, app_directory)
        doc_path = Path(quickweb.doc.__file__).parent
        required_files = doc_path.glob("*.md")
        base_required_files = [x.name for x in required_files]
        print(
            "** Adding startup files %s from %s"
            % (info(str(base_required_files)), info(doc_path))
        )
        for filename in required_files:
            shutil.copy(filename, app_directory)
        print_success("Application successfully created.")
        print_success("You can start it with:")
        print("    " + success("quickweb run " + app_directory))
        print_success("Or read about the app structure with:")
        print(
            "    "
            + success("more " + str(Path(app_directory, "QuickWeb_Application.md")))
        )
        print("**")
