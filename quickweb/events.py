#!/usr/bin/python
""" EVent management functions """
import sys

this = sys.modules[__name__]
this.handlers_map = {}


def invoke(name, *args, **kwargs):
    handlers_list = this.handlers_map.get(name, [])
    #  print('invoked', name, len(handlers_list))
    for handler in handlers_list:
        handler(*args, **kwargs)


def on_event(name, handler):
    #  print('event added for', name)
    handlers_list = this.handlers_map.get(name, [])
    handlers_list.append(handler)
    this.handlers_map[name] = handlers_list
