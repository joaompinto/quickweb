"""Installs QuickWeb using distutils

Run:
    python setup.py install

to install this package.
"""
from setuptools import setup, find_packages
from os.path import join

name = "QuickWeb"

desc = "Rapid Development Python Web Framework"
long_desc = "QuickWeb is a rapid web development python framework"


classifiers = """
Development Status :: 1 - Planning
Intended Audience :: Developers
License :: Freely Distributable
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python :: 3.7
Topic :: Internet :: WWW/HTTP :: WSGI
Topic :: Internet :: WWW/HTTP :: WSGI :: Application
Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware
Topic :: Internet :: WWW/HTTP :: WSGI :: Server
"""

requirements = open("requirements.txt").read()

setup(
    name=name,
    version=open(join("quickweb", "version")).readline().strip("\r\n"),
    description=desc,
    long_description=long_desc,
    author="João Pinto",
    author_email="lamego.pinto@gmail.com",
    classifiers=[x for x in classifiers.splitlines() if x],
    install_requires=[x for x in requirements.splitlines() if x],
    url="https://github.com/OpenPipe/QuickWeb",
    packages=find_packages(),
    package_data={"quickweb.doc": ["*"]},
    include_package_data=True,
    entry_points={"console_scripts": ["quickweb = quickweb.__main__:main"]},
)
