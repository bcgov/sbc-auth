#!/bin/sh

echo 'starting application'
gunicorn -b 0.0.0.0:8080 wsgi:application
