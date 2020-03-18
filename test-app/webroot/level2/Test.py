from quickweb import controller


class Controller(object):
    @controller.publish
    def default(self, *args, **kwargs):
        return "Python2"
