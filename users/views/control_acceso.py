# user views
# Django
import json

from django.contrib.auth import authenticate
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from datetime import date

from django.conf import settings
# Django decorators
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

# Models
from users.models import Persona

# Forms
from users.forms import LoginForm, SignupForm
from core.generic_save import add_user_with_profile


class LoginView(FormView):
    # login view
    template_name = 'control_acceso/sign-in.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión'
        return context

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            form = self.form_class(request.POST)
            if not form.is_valid():
                form_e = [{k: v[0]} for k, v in form.errors.items()]
                return JsonResponse({"result": False, "mensaje": 'Inicio de sesión fallido', "form": form_e})
            email=form.cleaned_data['email']
            user = authenticate(username=email, password=form.cleaned_data['password'])
            if not Persona.objects.filter(usuario=user):
                raise NameError('El usuario que intenta autenticar no dispone de perfil en esta aplicación.')
            persona = Persona.objects.get(usuario=user)
            perfil=persona.mi_perfil_principal()
            if not perfil:
                raise NameError('La cuenta que intenta iniciar sesión no dispone de un perfil activo.')
            request.session.set_expiry(240 * 60)
            login(self.request, user)
            request.session['persona'] = persona
            request.session['perfiles'] = persona.mis_perfilesusuarios()
            request.session['perfil'] = perfil
            request.session['modulo_categorias'] = ModuloCategoria.objects.filter(status=True)
            url_redirect = request.GET.get('next',reverse('users:home'))
            return JsonResponse({"result": True, "sessionid": request.session.session_key, 'url_redirect': url_redirect})
        except Exception as ex:
            transaction.set_rollback(True)
            return JsonResponse({"result": False, "mensaje": f'{ex}'})

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:home')  # redirigir a la página de inicio después del inicio de sesión
        return super().dispatch(request, *args, **kwargs)

class SignupView(FormView):
    # Signup con classe base view
    template_name = 'control_acceso/sign-up.html'
    form_class = SignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrate'
        return context

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            form = self.form_class(request.POST)
            if not form.is_valid():
                form_e = [{k: v[0]} for k, v in form.errors.items()]
                return JsonResponse({"result": False, "mensaje": 'Conflicto en formulario', "form": form_e})
            add_user_with_profile(request,form,'estudiante',form.cleaned_data.get('password'))
            # user = authenticate(email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password'))
            # login(self.request, user)
            url_redirect = request.GET.get('next', reverse('users:login'))
            return JsonResponse({"result": True, "sessionid": request.session.session_key, 'url_redirect': url_redirect})
        except Exception as ex:
            transaction.set_rollback(True)
            return JsonResponse({"result": False, "mensaje": f'{ex}'})


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    pass