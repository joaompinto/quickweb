from quickweb.server import controller


class Controller(object):
    @controller.publish
    def default(self, *args, **kwargs):
        return "INDEX OK"
