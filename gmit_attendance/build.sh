#!/usr/bin/env bash
# This script runs automatically on Render every time you deploy.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_admin
