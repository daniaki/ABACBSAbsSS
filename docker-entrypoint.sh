#!/bin/bash
set -e

###############################################################################
# Web project init
###############################################################################
echo "Running management commands."
python3 manage.py migrate
python3 manage.py populatetables
python3 manage.py collectstatic --noinput --clear

if [ "$ENVIRONMENT" = "production" ]; then
  gunicorn ABACBSAbsSS.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers="${GUNICORN_WORKERS}" \
    --threads="${GUNICORN_THREADS}" \
    --worker-class=gthread
else
  echo "I am ready!"
  tail -f /dev/null
fi
