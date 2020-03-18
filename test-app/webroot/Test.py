from quickweb import controller


class Controller(object):
    @controller.publish
    def default(self, *args, **kwargs):
        lower = kwargs.get("lower", "")
        lower = lower.upper()
        if len(args) == 1:
            lower += " with " + args[0]
        return "Python" + lower
