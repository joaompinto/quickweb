from quickweb.server import controller
from quickweb.app import modules


class Controller(object):
    @controller.publish
    def default(self, *args, **kwargs):
        return modules.test.hello()
