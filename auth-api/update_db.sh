#! /bin/sh
echo 'starting upgrade'
export DEPLOYMENT_ENV=migration
flask db upgrade