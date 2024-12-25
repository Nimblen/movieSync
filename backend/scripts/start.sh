#!/bin/bash


set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput --verbosity 0

# Start Gunicorn and Daphne
gunicorn config.wsgi:application --bind 0.0.0.0:8000 &
daphne -b 0.0.0.0 -p 8020 config.asgi:application &

# Wait for all background processes
wait


