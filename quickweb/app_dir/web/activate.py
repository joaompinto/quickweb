import cherrypy
from pathlib import Path
import quickweb.app
from quickweb.cli.colorhelper import print_error, info


def activate():
    """ Call the features setup function """

    features_list = list(Path(__file__).parent.joinpath("features").glob("*.py"))

    imported_features = []
    features_list_names = ", ".join(x.stem for x in features_list)
    print(f"** Setting up web features: {info(features_list_names)}")
    for module_fname in features_list:
        print(f"** Loading web feature {info(module_fname.stem)}")
        feature_dict = {}
        with open(module_fname) as source_file:
            exec(compile(source_file.read(), module_fname, "exec"), feature_dict)
        try:
            feature = feature_dict["Feature"]()
        except KeyError:
            print_error(
                "Feature module '%s' does not provide a Feature class!" % module_fname
            )
            exit(1)
        try:
            feature.setup()
        except:  # NOQA: E722
            print_error("Failed setting up feature '%s' !" % module_fname)
            raise
        imported_features.append(feature)

    for feature in imported_features:
        if hasattr(feature, "activate"):
            feature.activate()
    cherrypy.tree.mount(quickweb.app.root, config={})
