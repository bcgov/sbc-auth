#! /bin/sh
cd /opt/app-root
echo 'starting upgrade'
python3 manage.py db upgrade
