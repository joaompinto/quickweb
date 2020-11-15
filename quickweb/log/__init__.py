import os

SELECTED_LOG_LEVEL = int(os.environ.get("VERBOSE_LEVEL", "0"))


def verbose_log(log_level, msg):
    if log_level <= SELECTED_LOG_LEVEL:
        print(msg)
