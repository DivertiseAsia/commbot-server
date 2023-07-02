#!/usr/bin/env bash

pip install -r requirements.txt
playwright install firefox chromium
celery -A config worker -l INFO