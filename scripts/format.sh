#!/bin/sh -e

export SOURCE_FILES="lojaintegrada_scripts"

set -x

black $SOURCE_FILES
isort $SOURCE_FILES