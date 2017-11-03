from .base import *

DEBUG=False
ALLOWED_HOSTS = ['swainbot.herokuapp.com','127.0.0.1', '0.0.0.0']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

# Heroku: Update database configuration from $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
