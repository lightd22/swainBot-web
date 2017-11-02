from django.conf.urls import url
from . import views

app_name = 'predict'
urlpatterns = [
    url(r'^$', views.predict, name='predict'),
]
