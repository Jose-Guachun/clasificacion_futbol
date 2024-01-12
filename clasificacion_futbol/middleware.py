from django.shortcuts import redirect
from django.urls import reverse

from django.contrib.auth.models import User
from users.models import Persona

class BlockUrlsMiddleware:
    # Middleware de finalización de perfil.
    # Asegúrese de que cada usuario que interactúa con la plataformatienen su foto de perfil y biografía.
    def __init__(self, get_response):
        """inicializacion del middleware"""
        self.get_response = get_response

    def __call__(self, request):
        """Código a ejecutar para cada solicitud antes de que se llame a
            la vista."""
        if not request.user.is_anonymous:
            #if not request.user.is_staff:
            dosfactores=request.session['dosfactores']
            autenticado=request.session['autenticado']
            if not dosfactores or autenticado:
                if request.path in [reverse('users:signup'), reverse('users:login'), reverse('users:validate_token')]:
                    return redirect('users:home')
            else:
                if request.path in [reverse('users:signup'),
                                    reverse('users:login'),
                                    reverse('users:usuarios'),
                                    reverse('users:home'),
                                    reverse('clubes:gestion_clubes'),]:
                        return redirect('users:validate_token')
        response = self.get_response(request)
        return response
