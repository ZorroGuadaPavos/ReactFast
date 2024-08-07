#! /usr/bin/env bash

set -a; source .env.local; set +a;
export PYTHONPATH=$(pwd)

python src/backend_pre_start.py

# Run migrations
alembic upgrade head

# # Create initial data in DB
python src/initial_data.py