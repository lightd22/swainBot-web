from .base import *

DEBUG=False
ALLOWED_HOSTS = ['swainbot.herokuapp.com','127.0.0.1']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)
