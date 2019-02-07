#!/bin/sh
set -eu
rm -rf _build
make html
cd _build/html/ && zip ../../html_docs.zip -r .
