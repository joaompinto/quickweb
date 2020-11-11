from quickweb import controller


def render():
    return {"var": controller.lib.test.hello()}
