#!/bin/python

import os
import sys
import time
from glob import glob
from os.path import join
import subprocess

TEST_PORT = 8999

os.environ["PORT"] = str(TEST_PORT)
os.environ["TEST_MODE"] = "1"


test_specs = glob(join("test-app", "tests", "*.yaml"))


subp = subprocess.Popen(
    [sys.executable, "-m", "quickweb", "run", "test-app"], close_fds=True
)

print("Waiting 1s for the server warmup")
# Allow 1s for the process to start
time.sleep(1)


for test_filename in test_specs:
    http_unit_test = join("quickweb", "http_unit_test.py")
    cmd = sys.executable + " %s http://127.0.0.1:%d %s" % (
        http_unit_test,
        TEST_PORT,
        test_filename,
    )
    rc = os.system(cmd)
    if rc != 0:
        subp.terminate()
        exit(2)

subp.terminate()
