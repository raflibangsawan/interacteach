release: python createsuperuser.py
web: python manage.py collectstatic --no-input && python manage.py migrate && gunicorn interacteach.wsgi
