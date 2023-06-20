#!/usr/bin/env bash

echo "Cards server boot!"
playwright install firefox
gunicorn config.wsgi --log-file -