#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python manage.py runserver &
sleep 2
xdg-open http://127.0.0.1:8000/
wait