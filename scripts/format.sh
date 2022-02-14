#!/bin/sh -e

export SOURCE_FILES="lojaintegrada_scripts"

set -x

isort $SOURCE_FILES
black $SOURCE_FILES