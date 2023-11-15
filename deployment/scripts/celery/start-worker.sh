#!/bin/bash

set -o errexit
set -o nounset

python3 /usr/local/lib/python3.11/site-packages/watchdog/watchmedo.py auto-restart -d agenda_culturel -p '*.py' --recursive -- celery -A "$APP_NAME" worker -l info
