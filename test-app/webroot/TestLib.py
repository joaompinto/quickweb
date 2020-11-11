from quickweb import controller


class Controller(object):
    @controller.publish
    def default(self, *args, **kwargs):
        return controller.lib.test.hello()
