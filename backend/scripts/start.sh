
set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput --verbosity 0

gunicorn config.wsgi:application --bind 0.0.0.0:8000 &
daphne -b 0.0.0.0 -p 8020 config.asgi:application
wait