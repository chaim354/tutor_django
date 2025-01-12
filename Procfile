release: python manage.py collectstatic --noinput
web: gunicorn web_project.wsgi:application