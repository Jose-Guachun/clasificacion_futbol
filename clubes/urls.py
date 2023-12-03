# Users Urls

# Django
from django.urls import path, re_path

# importaciones de apps
from clubes import gestion_clubes

urlpatterns = [
    # CONTROL USUARIOS
    re_path(r'^gestion_clubes$', gestion_clubes.ViewSet.as_view(), name='gestion_clubes'),
]