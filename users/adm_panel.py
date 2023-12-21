from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from datetime import date, datetime

from pyexpat.errors import messages

from clubes.models import PagoRubroTarjeta, Partido, Club, IntegranteClub, TipoPartido, Fase, TipoPartidoFase, Torneo
from core.funciones import Paginacion, generar_nombre_file
from users.forms import PagoTarjetaForm
from users.models import Persona
from users.templatetags.extra_tags import encrypt
from django.template.loader import get_template


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

        elif action == 'goleadores':
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

        elif action == 'pagos': 
            try:
                context['title']='Subir evidencia'
                context['codigo']= codigo = request.GET.get('codigo','')
                url_vars, torneo, filtro = f'&action={action}&codigo={codigo}',  request.GET.get('torneof',''), Q(equipo__codigo=codigo, status=True)
                if torneo:
                    filtro=filtro & Q(torneo_id=torneo)
                    url_vars+=f'&torneo={torneo}'
                    context['torneo']=int(torneo)
                pagos=PagoRubroTarjeta.objects.filter(filtro)
                paginator = Paginacion(pagos, 50)
                page = int(request.GET.get('page', 1))
                paginator.rangos_paginado(page)
                context['paging'] = paging = paginator.get_page(page)
                context['listado'] = paging.object_list
                context['url_vars'] = url_vars
                context['torneos'] = Torneo.objects.filter(status=True)
                return render(request, 'planificacion/pagos.html', context)
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
                
        elif action == 'addpago':
            try:
                form = PagoTarjetaForm()
                context['form'] = form
                template = get_template('base_ajax_form_modal.html')
                return JsonResponse({'result': True, 'data': template.render(context)})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

        elif action == 'editpago':
            try:
                context['id'] = id = int(encrypt(request.GET['id']))
                pago = PagoRubroTarjeta.objects.get(id=id)
                context['form'] = PagoTarjetaForm(instancia=pago, initial=model_to_dict(pago))
                template = get_template('base_ajax_form_modal.html')
                return JsonResponse({'result': True, 'data': template.render(context)})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
        
        elif action == 'resultados':
            try:
                context['id'] = id = int(encrypt(request.GET['id']))
                context['partido'] = Partido.objects.get(id=id)
                template = get_template('adm_panel/resultados.html')
                return JsonResponse({'result': True, 'data': template.render(context)})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
        
        elif action == 'partidos':
            try:
                context['title'] = 'Inicio'
                url_vars, filtros, categoria, tipopartido, fase, torneo, inicio, fin = f'&action={action}', Q(status=True), \
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
            except:
                messages.error(request, f'Error: {ex}')  
                     
        else:
            try:
                context['title'] = 'Inicio'
                return render(request, 'adm_panel/inicio.html', context)
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
        

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        if action == 'addpago':
            try:
                form = PagoTarjetaForm(request.POST, request.FILES)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                newfile = form.cleaned_data['archivo']
                equipo = form.cleaned_data['equipo']
                if newfile:
                    extension = newfile._name.split('.')
                    exte = extension[len(extension) - 1]
                    if newfile.size > 2194304:
                        raise NameError(u"El tamaño del archivo es mayor a 2 Mb.")
                    if not exte.lower() in ['png', 'jpg', 'jpeg', 'pdf', 'xml']:
                        raise NameError(u"Solo se permite archivos de formato .png, .jpg, .jpeg, .pdf, .xml")
                    newfile._name = generar_nombre_file(f'comprobante_{equipo.id}_', newfile._name)
                pago = PagoRubroTarjeta(equipo=equipo,
                                        torneo=form.cleaned_data['torneo'],
                                        valor=form.cleaned_data['valor'],
                                        archivo=newfile)
                pago.save()
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'editpago':
            try:
                pago = PagoRubroTarjeta.objects.get(id=int(encrypt(request.POST['id'])))
                form = PagoTarjetaForm(request.POST, request.FILES, instancia=pago)
                form.fields['archivo'].required=False
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                newfile = form.cleaned_data['archivo']
                if newfile:
                    extension = newfile._name.split('.')
                    exte = extension[len(extension) - 1]
                    if newfile.size > 2194304:
                        raise NameError(u"El tamaño del archivo es mayor a 2 Mb.")
                    if not exte.lower() in ['png', 'jpg', 'jpeg', 'pdf', 'xml']:
                        raise NameError(u"Solo se permite archivos de formato .png, .jpg, .jpeg, .pdf, .xml")
                    newfile._name = generar_nombre_file(f'escudo', newfile._name)
                    pago.archivo = newfile
                pago.equipo = form.cleaned_data['equipo']
                pago.torneo = form.cleaned_data['torneo']
                pago.valor = form.cleaned_data['valor']
                pago.save()
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'delpago':
            try:
                pers = PagoRubroTarjeta.objects.get(id=int(encrypt(request.POST['id'])))
                pers.status = False
                pers.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})
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
