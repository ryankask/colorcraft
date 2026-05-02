#!/bin/bash
set -e

if [ "$FLASK_ENV" = "development" ]; then
    echo "Starting in development mode with Flask dev server..."
    exec python -m colorcraft.web_app
else
    echo "Starting in production mode with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 colorcraft.web_app:app
fi
