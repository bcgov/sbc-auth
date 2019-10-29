#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
PYTHONPATH=./src alembic upgrade head
