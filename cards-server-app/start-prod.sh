#!/usr/bin/env bash

echo "Cards server production start!"
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py init_super_user
gunicorn --bind :8001 config.wsgi:application --daemon --workers 3 --threads=3 --worker-class=gthread --worker-tmp-dir /dev/shm --timeout 120 --capture-output --enable-stdio-inheritance --log-level warning
nginx -g "daemon off;"