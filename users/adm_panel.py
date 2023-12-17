from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from datetime import date, datetime

from pyexpat.errors import messages

from clubes.models import Partido, Club, IntegranteClub, TipoPartido, Fase, TipoPartidoFase, Torneo
from core.funciones import Paginacion
from users.models import Persona
from users.templatetags.extra_tags import encrypt


class MainView(View):
    # User detail view
    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action', '')
        if action == 'posiciones':
            try:
                context['title'] = 'Tabla de posiciones'

                filtro, url_vars, torneo = Q(status=True), \
                                                     f'&action={action}', \
                                                     request.GET.get('torneo', '')
                if not torneo:
                    torneo = Torneo.objects.filter(status=True).last()
                else:
                    torneo = Torneo.objects.get(id=torneo)

                equipos = torneo.equipos.all()
                # PAGINADOR
                paginator = Paginacion(equipos, 50)
                page = int(request.GET.get('page', 1))
                paginator.rangos_paginado(page)
                context['paging'] = paging = paginator.get_page(page)
                context['listado'] = paging.object_list
                context['url_vars'] = url_vars
                context['torneo'] = torneo
                context['torneos'] = Torneo.objects.filter(status=True)
                return render(request, 'adm_panel/tabla_posiciones.html', context)
            except Exception as ex:
                messages.error(request, f'Error: {ex}')

        if action == 'goleadores':
            try:
                context['title'] = 'Goleadores'

                filtro, url_vars, torneo = Q(status=True), \
                                                     f'&action={action}', \
                                                     request.GET.get('torneo', '')
                if not torneo:
                    torneo = Torneo.objects.filter(status=True).last()
                else:
                    torneo = Torneo.objects.get(id=torneo)

                goleadores = torneo.goleadores()
                # PAGINADOR
                paginator = Paginacion(goleadores, 50)
                page = int(request.GET.get('page', 1))
                paginator.rangos_paginado(page)
                context['paging'] = paging = paginator.get_page(page)
                context['listado'] = paging.object_list
                context['url_vars'] = url_vars
                context['torneo'] = torneo
                context['torneos'] = Torneo.objects.filter(status=True)
                return render(request, 'adm_panel/goleadores.html', context)
            except Exception as ex:
                messages.error(request, f'Error: {ex}')

        else:
            context['title'] = 'Inicio'
            url_vars, filtros, categoria, tipopartido, fase, torneo, inicio, fin = '', Q(status=True), \
                                                                        request.GET.get('categoria', ''), \
                                                                        request.GET.get('tipopartido', ''), \
                                                                        request.GET.get('fase', ''), \
                                                                        request.GET.get('torneo', ''),\
                                                                        request.GET.get('inicio', ''),\
                                                                        request.GET.get('fin', '')
            if categoria:
                context['categoria'] = categoria=int(categoria)
                filtros = filtros & Q(torneo__generotorneo=categoria)
                url_vars += f"&categoria={categoria}"

            if torneo:
                context['torneo'] = torneo = int(torneo)
                filtros = filtros & Q(torneo_id=torneo)
                url_vars += f"&torneo={torneo}"

            if tipopartido:
                context['tipopartido'] = tipopartido = int(tipopartido)
                filtros = filtros & Q(tipopartido_id=tipopartido)
                url_vars += f"&tipopartido={tipopartido}"

            if fase:
                context['fase'] = fase = int(fase)
                filtros = filtros & Q(tipopartidofase__fase_id=fase)
                url_vars += f"&fase={fase}"

            if inicio:
                context['inicio'] = inicio
                filtros = filtros & Q(fecha__gte=inicio)
                url_vars += f"&inicio={inicio}"

            if fin:
                context['fin'] = fin
                filtros = filtros & Q(fecha__lte=fin)
                url_vars += f"&fin={fin}"

            partidos = Partido.objects.filter(filtros)
            paginator = Paginacion(partidos, 10)
            page = int(request.GET.get('page', 1))
            paginator.rangos_paginado(page)
            context['paging'] = paging = paginator.get_page(page)
            context['listado'] = paging.object_list
            context['url_vars'] = url_vars
            context['tipos'] = TipoPartido.objects.filter(status=True)
            context['torneos'] = Torneo.objects.filter(status=True)
            context['fases'] = Fase.objects.filter(status=True)
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
