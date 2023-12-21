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
from django.contrib.auth.decorators import login_required

from django.conf import settings
# Django decorators
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from core.mail import send_email

# Models
from users.models import Persona

# Forms
from users.forms import LoginForm, SignupForm
from core.generic_save import add_user_with_profile
from core.funciones import generarcodigoacceso

@login_required
def validate_token(request):
    context={}
    persona= Persona.objects.get(usuario=request.user)
    if request.method=='POST':
        token=request.POST.get('token')
        code=persona.codigoacceso   
        if token == code:
            persona.autenticado=True
            persona.save()
            request.session['autenticado'] = persona.autenticado
            url_redirect = request.GET.get('next',reverse('users:home'))
            return JsonResponse({'result':True,'url_redirect':url_redirect})
        else:
            mensaje='El codigo ingresado no es el correcto'
            return JsonResponse({'result':False,'mensaje':mensaje})
    context['persona']=persona
    context['title']='Validar código'
    return render(request, 'control_acceso/validate_token.html', context)


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
            username=form.cleaned_data['username']
            user = authenticate(username=username, password=form.cleaned_data['password'])
            if not Persona.objects.filter(usuario=user):
                raise NameError('El usuario que intenta autenticar no dispone de perfil en esta aplicación.')
            persona = Persona.objects.get(usuario=user)
            if persona.dosfactores:
                persona.codigoacceso = generarcodigoacceso(persona) 
                persona.autenticado = False
                persona.save(request)
                send_email('Acceso al sistema Fcunemi', f'Su código de acceso es el siguiente {persona.codigoacceso}', 
                           persona.email, persona,'correo_v2.html')
            
            login(self.request, user)
            # request.session['persona'] = persona
            request.session['perfil'] = persona.perfil
            request.session['autenticado'] = persona.autenticado
            request.session['dosfactores'] = persona.dosfactores
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
            add_user_with_profile(request,form,1,form.cleaned_data.get('password'))
            # user = authenticate(username=form.cleaned_data.get('email'), password=form.cleaned_data.get('password'))
            # login(self.request, user)
            url_redirect = request.GET.get('next', reverse('users:login'))
            return JsonResponse({"result": True, "sessionid": request.session.session_key, 'url_redirect': url_redirect})
        except Exception as ex:
            transaction.set_rollback(True)
            return JsonResponse({"result": False, "mensaje": f'{ex}'})


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):

    def dispatch(self, request, *args, **kwargs):
        # Realiza tus acciones antes de cerrar sesión
        persona = request.user.persona_set.get()
        persona.autenticado = False
        persona.save()

        # Llama al método dispatch de la clase padre para continuar con el proceso de cierre de sesión
        return super().dispatch(request, *args, **kwargs)
    