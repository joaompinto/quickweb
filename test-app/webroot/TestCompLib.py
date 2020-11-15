from quickweb.server import controller


def render():
    return {"var": controller.lib.test.hello()}
