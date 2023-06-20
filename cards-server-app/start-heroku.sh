#!/usr/bin/env bash

echo "Cards server booting!"
playwright install firefox
gunicorn config.wsgi --log-file -