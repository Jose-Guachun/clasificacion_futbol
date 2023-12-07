# Users Urls

# Django
from django.urls import path, re_path

# importaciones de apps
from core import api

urlpatterns = [
    # CONTROL USUARIOS
    re_path(r'^api', api.ViewSet.as_view(), name='api'),
]