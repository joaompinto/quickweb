""" Provides some modules supportings functions """
from fnmatch import fnmatch


def fnmatch_list(filename, pattern_list):
    """ Check filename against a list of patterns using fnmatch """
    if type(pattern_list) != list:
        pattern_list = [pattern_list]
    for pattern in pattern_list:
        if fnmatch(filename, pattern):
            return True
    return False
