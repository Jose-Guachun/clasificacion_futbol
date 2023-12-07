from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from datetime import date, datetime

from clubes.models import Partido, Club, IntegranteClub, TipoPartido, Fase, TipoPartidoFase
from core.funciones import Paginacion
from users.models import Persona


class MainView(LoginRequiredMixin, View):
    # User detail view
    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action', '')
        if action == 'home':
            try:
                context['title'] = 'Inicio'
                # request.session['viewactivo'] = 1
                template_name = 'adm_panel/home.html'
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": str(ex)})
        else:
            context['title'] = 'Inicio'
            url_vars = ''
            partidos = Partido.objects.filter(status=True)
            paginator = Paginacion(partidos, 10)
            page = int(request.GET.get('page', 1))
            paginator.rangos_paginado(page)
            context['paging'] = paging = paginator.get_page(page)
            context['listado'] = paging.object_list
            context['url_vars'] = url_vars
            context['torneos'] = TipoPartido.objects.filter(status=True)
            context['fases'] = TipoPartidoFase.objects.filter(status=True)
            template_name = 'adm_panel/home_anonymous.html'
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        if action == 'signup':
            form = self.form_class(request.POST)
            if form.is_valid():
                # <process form cleaned data>
                return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class HomeView(LoginRequiredMixin, View):
    # User detail view
    template_name = 'adm_panel/home.html'

    def get(self, request, *args, **kwargs):
        context = {}
        hoy=datetime.now()
        context['viewactivo'] = 'home'
        context['usuario'] = request.user
        context['persona'] = request.user.persona_set.get(status=True)
        try:
            context['title'] = 'Inicio'
            context['partidos'] = len(Partido.objects.filter(status=True))
            context['partidos_pendientes'] = len(Partido.objects.filter(status=True, fecha__gte=hoy))
            context['equipos'] = len(Club.objects.filter(status=True))
            context['jugadores'] = len(IntegranteClub.objects.filter(status=True))
            context['usuarios'] = len(Persona.objects.filter(status=True, perfil__in=[1, 2, 3, 4]))
            context['administradores'] = len(Persona.objects.filter(status=True, perfil=1))
        except Exception as ex:
            transaction.set_rollback(True)
            return JsonResponse({"result": False, "mensaje": str(ex)})
        return render(request, self.template_name, context)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        persona = request.session['persona']
        if action == 'signup':
            form = self.form_class(request.POST)
            if form.is_valid():
                # <process form cleaned data>
                return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
