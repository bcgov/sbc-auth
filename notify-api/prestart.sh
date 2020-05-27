#! /usr/bin/env bash

#set env variables from file if exists
if [ -f /app/config/config.env ]; then
    set -a
    . /app/config/config.env
    env
fi

# Let the DB start
sleep 10;
# Run migrations
PYTHONPATH=./src alembic upgrade head
