release: python manage.py migrate
web: ddtrace-run gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker

