release: python manage.py migrate && python manage.py collectstatic --no-input
web: gunicorn gmit_project.wsgi:application --bind 0.0.0.0:$PORT
