#!/bin/bash

set -xv
set -o nounset
set -o errexit
set -o pipefail
set -o noclobber

export IFS=$' \t\n'
export LANG=C.UTF-8
umask u=rwx,g=,o=

.venv/bin/python3 -m pyflakes src
.venv/bin/python3 -m mypy src
.venv/bin/python3 -m black --check src
.venv/bin/python3 -m isort --check-only src
.venv/bin/python3 -m pytest src
