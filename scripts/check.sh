#!/bin/sh -e

export SOURCE_FILES="lojaintegrada_scripts"

set -x

isort --check --diff $SOURCE_FILES
black --check --diff $SOURCE_FILES
flake8 $SOURCE_FILES
mypy $SOURCE_FILES