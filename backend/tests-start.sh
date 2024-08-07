#! /usr/bin/env bash

export PYTHONPATH=$(pwd)

set -e
set -x

alembic upgrade head

python src/tests_pre_start.py

bash ./scripts/test.sh "$@"
