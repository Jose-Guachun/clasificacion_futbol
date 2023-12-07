# Users Urls

# Django
from django.urls import path, re_path

# importaciones de apps
from users import control_acceso, adm_panel, adm_users

urlpatterns = [
    # PANTALLAS PRINCIPALES
    re_path(r'^$',adm_panel.HomeView.as_view(), name='home'),
    re_path(r'^main$', adm_panel.MainView.as_view(), name='main'),

    # ACCESO AL SISTEMA
    re_path(r'^login$',control_acceso.LoginView.as_view(), name='login'),
    re_path(r'^signup$',control_acceso.SignupView.as_view(), name='signup'),
    re_path(r'^logout$',control_acceso.LogoutView.as_view(), name='logout'),

    # CONTROL USUARIOS
    re_path(r'^usuarios$', adm_users.ViewSet.as_view(), name='usuarios'),

    # re_path(r'^administrativos$', administrativos.ViewSet.as_view(), name='administrativos'),
    # # re_path(r'^estudiantes$', estudiantes.ViewSet.as_view(), name='estudiantes'),
    # re_path(r'^docentes$', docentes.ViewSet.as_view(), name='docentes'),
]