import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, Sum
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from core.mail import send_email
from users.models import Persona, Provincia, Pais, Ciudad
from users.templatetags.extra_tags import encrypt
from core.funciones import Paginacion, filtro_persona_generico, filtro_persona_generico_principal, generar_nombre_file
from core.generic_save import add_user_with_profile, edit_persona_with_profile, gestionarusuario
from clubes.models import Club, IntegranteClub, TIPO_ROL, PagoRubroTarjeta, Partido, TipoPartido, TipoPartidoFase, TarjetaPartido, Torneo, GolPartido, ResultadoPartido
from clubes.forms import ClubForm, IntegranteForm, PartidoForm, TarjetaForm, TorneoForm, GolForm


class ViewSet(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action')
        context['persona'] = request.user.persona_set.get(status=True)
        context['viewactivo'] = 'clubes'
        if action:
            if action == 'addclub':
                try:
                    context['form'] = ClubForm()
                    template = get_template('base_ajax_form_modal.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'editclub':
                try:
                    context['id'] = id = int(encrypt(request.GET['id']))
                    club = Club.objects.get(id=id)
                    context['form'] = ClubForm(instancia=club, initial=model_to_dict(club))
                    template = get_template('base_ajax_form_modal.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'integrantes':
                try:
                    context['title'] = 'Integrantes'
                    id = request.GET['id']
                    club = Club.objects.get(pk=int(encrypt(id)))
                    filtro, url_vars, search, rol = Q(status=True, club=club), f'&action={action}&id={id}', request.GET.get('s', ''), request.GET.get('rol', '')
                    if rol:
                        context['rol'] = rol = int(rol)
                        url_vars += f'&rol={rol}'
                        filtro = filtro & Q(rol=rol)
                    if search:
                        context['s'] = search
                        url_vars += '&s=' + search
                        filtro = filtro_persona_generico(filtro, search)

                    cursos = IntegranteClub.objects.filter(filtro)
                    # PAGINADOR
                    paginator = Paginacion(cursos, 10)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['club'] = club
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    context['url_vars'] = url_vars
                    context['roles'] = TIPO_ROL
                    return render(request, 'clubes/integrantes.html', context)
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'addintegrante':
                try:
                    context['title'] = 'Adicionar integrante'
                    context['club'] = Club.objects.get(id=int(encrypt(request.GET['id'])))
                    form = IntegranteForm()
                    form.fields['provincia'].queryset = Provincia.objects.none()
                    form.fields['ciudad'].queryset = Ciudad.objects.none()
                    context['form'] = form
                    return render(request, 'clubes/formularios/formintegrantes.html', context)
                except Exception as ex:
                    messages.error(request, f'{ex}')

            elif action == 'editintegrante':
                try:
                    context['title'] = f'Editar integrante'
                    context['id'] = id = int(encrypt(request.GET['id']))
                    context['integrante'] = integrante = IntegranteClub.objects.get(id=id)
                    context['club'] = integrante.club
                    pers = integrante.persona
                    d_iniciales = {}
                    d_iniciales.update(model_to_dict(integrante))
                    d_iniciales.update(model_to_dict(pers))
                    form = IntegranteForm(instancia=integrante, initial=d_iniciales)
                    form.fields['provincia'].queryset = pers.pais.provincias() if pers.pais else Provincia.objects.none()
                    form.fields['ciudad'].queryset = pers.provincia.ciudades() if pers.provincia else Ciudad.objects.none()
                    context['form'] = form
                    form.edit()
                    return render(request, 'clubes/formularios/formintegrantes.html', context)
                except Exception as ex:
                    messages.error(request, f'{ex}')

            elif action == 'partidos':
                try:
                    context['title'] = 'Partidos'
                    idtorneo = request.GET['id']
                    torneo = Torneo.objects.get(id=int(encrypt(idtorneo)))
                    filtro, url_vars, search, tipopartido, fase, fecha = Q(status=True, torneo=torneo), \
                                                                         f'&action={action}&id={idtorneo}', \
                                                                         request.GET.get('s', ''), \
                                                                         request.GET.get('tipopartido', ''), \
                                                                         request.GET.get('fase', ''), \
                                                                         request.GET.get('fecha', '')
                    if tipopartido:
                        context['tipopartido'] = tipopartido = int(tipopartido)
                        url_vars += f'&tipopartido={tipopartido}'
                        filtro = filtro & Q(tipopartidofase__tipopartido_id=tipopartido)

                    if fase:
                        context['fase'] = fase = int(fase)
                        url_vars += f'&fase={fase}'
                        filtro = filtro & Q(tipopartidofase_id=fase)

                    if search:
                        context['s'] = search
                        url_vars += '&s=' + search
                        filtro = filtro & (Q(clublocal__nombre__icontains=search) | Q(clubvisitante__nombre__icontains=search))

                    cursos = Partido.objects.filter(filtro)
                    # PAGINADOR
                    paginator = Paginacion(cursos, 10)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    context['url_vars'] = url_vars
                    context['tipopartidos'] = TipoPartido.objects.filter(id__in=torneo.tipopartidos.all().values_list('id', flat=True))
                    context['torneo'] = torneo
                    context['viewactivo'] = 'partidos'
                    return render(request, 'planificacion/view.html', context)
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'addpartido':
                try:
                    form = PartidoForm()
                    torneo = Torneo.objects.get(id=int(request.GET['idp']))
                    form.fields['tipopartido'].queryset = TipoPartido.objects.filter(id__in=torneo.tipopartidos.all().values_list('id', flat=True))
                    form.fields['tipopartidofase'].queryset = TipoPartidoFase.objects.none()
                    form.fields['clubvisitante'].queryset = Club.objects.filter(tipoequipo=torneo.generotorneo, status=True)
                    form.fields['clublocal'].queryset = Club.objects.filter(tipoequipo=torneo.generotorneo, status=True)
                    context['form'] = form
                    context['idp'] = request.GET['idp']
                    template = get_template('planificacion/formularios/formpartidos.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'editpartido':
                try:
                    context['id'] = id = int(encrypt(request.GET['id']))
                    instancia = Partido.objects.get(id=id)
                    form = PartidoForm(instancia=instancia,
                                       initial={'clublocal': instancia.clublocal,
                                                'clubvisitante': instancia.clubvisitante,
                                                'tipopartidofase': instancia.tipopartidofase,
                                                'tipopartido': instancia.tipopartido,
                                                'fecha': instancia.fecha.date(),
                                                'hora': instancia.fecha.time()})
                    form.fields['tipopartido'].queryset = TipoPartido.objects.filter(id__in=instancia.torneo.tipopartidos.all().values_list('id', flat=True))
                    form.fields['tipopartidofase'].queryset = TipoPartidoFase.objects.filter(tipopartido=instancia.tipopartido)
                    context['form'] = form
                    template = get_template('planificacion/formularios/formpartidos.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'registrargoles':
                try:
                    context['id'] = id = int(encrypt(request.GET['id']))
                    context['partido'] = Partido.objects.get(id=id)
                    template = get_template('clubes/formularios/formgoles.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'cargarequipos':
                try:
                    id = int(request.GET['id'])
                    clubes = Club.objects.filter(status=True).exclude(id=id)
                    resp = [{'value': qs.pk, 'text': f"{qs.nombre}"}
                            for qs in clubes]
                    return JsonResponse({'result': True, 'data': resp})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'cargarfases':
                try:
                    id = int(request.GET['id'])
                    fases = TipoPartidoFase.objects.filter(status=True, tipopartido_id=id)
                    resp = [{'value': qs.pk, 'text': f"{qs.fase.nombre}"}
                            for qs in fases]
                    return JsonResponse({'result': True, 'data': resp})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'registrartarjeta':
                try:
                    partido = Partido.objects.get(id=int(encrypt(request.GET['id'])))
                    lista = [partido.clublocal.id, partido.clubvisitante.id]
                    form = TarjetaForm()
                    form.fields['integrante'].queryset = IntegranteClub.objects.none()
                    form.fields['club'].queryset = Club.objects.filter(id__in=lista)
                    context['form'] = form
                    context['id'] = partido.id
                    template = get_template('planificacion/formularios/formtarjeta.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'registrargol':
                try:
                    partido = Partido.objects.get(id=int(encrypt(request.GET['id'])))
                    lista = [partido.clublocal.id, partido.clubvisitante.id]
                    form = GolForm()
                    form.fields['integrante'].queryset = IntegranteClub.objects.none()
                    form.fields['club'].queryset = Club.objects.filter(id__in=lista)
                    context['form'] = form
                    context['id'] = partido.id
                    template = get_template('planificacion/formularios/formtarjeta.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'cargarintegrantes':
                try:
                    id = int(request.GET['id'])
                    integrantes = IntegranteClub.objects.filter(status=True, club_id=id)
                    resp = [{'value': qs.pk, 'text': f"{qs.persona}"}
                            for qs in integrantes]
                    return JsonResponse({'result': True, 'data': resp})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'detalletarjetas':
                try:
                    partido = Partido.objects.get(id=int(encrypt(request.GET['id'])))
                    lista = [partido.clublocal.id, partido.clubvisitante.id]
                    form = TarjetaForm()
                    form.fields['hora'].initial = datetime.now().time().strftime('%H:%M')
                    form.fields['integrante'].queryset = IntegranteClub.objects.none()
                    form.fields['club'].queryset = Club.objects.filter(id__in=lista)
                    context['form'] = form
                    context['id'] = partido.id
                    template = get_template('planificacion/formularios/formtarjeta.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'torneos':
                try:
                    context['title'] = 'Torneos planificados'
                    filtro, url_vars, search = Q(status=True), \
                                               f'&action={action}', \
                                               request.GET.get('s', ''),

                    if search:
                        context['s'] = search
                        url_vars += '&s=' + search
                        filtro = filtro & Q(nombre__icontains=search)

                    torneos = Torneo.objects.filter(filtro)
                    # PAGINADOR
                    paginator = Paginacion(torneos, 10)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    context['url_vars'] = url_vars
                    context['viewactivo'] = 'partidos'
                    return render(request, 'planificacion/torneos.html', context)
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'addtorneo':
                try:
                    form = TorneoForm()
                    context['form'] = form
                    context['torneo'] = False
                    context['seccionado'] = True
                    context['tipopartidos'] = TipoPartido.objects.filter(status=True)
                    template = get_template('planificacion/formularios/formtorneo.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'edittorneo':
                try:
                    context['id'] = id = int(encrypt(request.GET['id']))
                    instancia = Torneo.objects.get(id=id)
                    form = TorneoForm(instancia=instancia,
                                      initial={'nombre': instancia.nombre,
                                               'inicio': instancia.inicio.date(),
                                               'fin': instancia.fin.date(),
                                               'generotorneo':instancia.generotorneo})
                    context['tipopartidos'] = TipoPartido.objects.filter(status=True)
                    context['form'] = form
                    context['seccionado'] = True
                    context['torneo'] = instancia
                    template = get_template('planificacion/formularios/formtorneo.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'posiciones':
                try:
                    context['title'] = 'Tabla de posiciones'
                    idtorneo = request.GET['id']
                    torneo = Torneo.objects.get(id=int(encrypt(idtorneo)))
                    filtro, url_vars, search, tipopartido, fase, fecha = Q(status=True, torneo=torneo), \
                                                                         f'&action={action}&id={idtorneo}', \
                                                                         request.GET.get('s', ''), \
                                                                         request.GET.get('tipopartido', ''), \
                                                                         request.GET.get('fase', ''), \
                                                                         request.GET.get('fecha', '')

                    if search:
                        context['s'] = search
                        url_vars += '&s=' + search
                        filtro = filtro & Q(nombre__icontains=search)
                    equipos = torneo.equipos.all()
                    # PAGINADOR
                    paginator = Paginacion(equipos, 50)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    context['url_vars'] = url_vars
                    context['torneo'] = torneo
                    context['viewactivo'] = 'partidos'
                    return render(request, 'planificacion/posiciones.html', context)
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

            elif action == 'cargarequiposfiltrado':
                try:
                    genero = int(request.GET['value'])
                    torneo = request.GET.get('args','')
                    clubes = Club.objects.filter(status=True, tipoequipo=genero)
                    resp = [{'value': qs.pk,
                             'text': f"{qs.nombre.title()}",
                             'check': 'checked' if not torneo or qs.club_in_torneo(torneo) else '',
                             'img': qs.get_escudo_img_sm()}
                            for qs in clubes]
                    return JsonResponse({'result': True, 'data': resp})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            elif action == 'resultados':
                try:
                    context['id'] = id = int(encrypt(request.GET['id']))
                    context['partido'] = Partido.objects.get(id=id)
                    template = get_template('clubes/formularios/resultados.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
                
            elif action == 'validarpagos':
                try:
                    context['id'] = id = int(encrypt(request.GET['id']))
                    context['pago'] = pago = PagoRubroTarjeta.objects.get(id=id)
                    context['tarjetas'] = TarjetaPartido.objects.filter(status=True, club=pago.equipo, partido__torneo=pago.torneo, pagado=False)
                    template = get_template('clubes/formularios/pagosrubros.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
        
            elif action == 'comprobantes':
                try:
                    context['title'] = 'Comprobantes'
                    idclub = request.GET['id']
                    idtorneo = request.GET['idp']
                    torneo = Torneo.objects.get(id=int(encrypt(idtorneo)))
                    equipo = Club.objects.get(id=int(encrypt(idclub)))
                    filtro, url_vars= Q(status=True, torneo=torneo, equipo=equipo), \
                                        f'&action={action}&idp={idtorneo}&id={idclub}'
                    # PAGINADOR
                    pagos=PagoRubroTarjeta.objects.filter(filtro)
                    paginator = Paginacion(pagos, 20)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    context['url_vars'] = url_vars
                    context['torneo'] = torneo
                    context['equipo'] = equipo
                    context['tarjetas'] = TarjetaPartido.objects.filter(status=True, club=equipo, partido__torneo=torneo, pagado=False)
                    context['viewactivo'] = 'partidos'
                    return render(request, 'planificacion/comprobantes.html', context)
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')

        else:
            try:
                context['title'] = 'Equipos'
                filtro, url_vars, search = Q(status=True), f'', request.GET.get('s')
                if search:
                    context['s'] = search
                    url_vars += '&s=' + search
                    filtro = filtro & Q(nombre__icontains=search)

                cursos = Club.objects.filter(filtro)
                # PAGINADOR
                paginator = Paginacion(cursos, 10)
                page = int(request.GET.get('page', 1))
                paginator.rangos_paginado(page)
                context['paging'] = paging = paginator.get_page(page)
                context['listado'] = paging.object_list
                return render(request, 'clubes/view.html', context)
            except Exception as ex:
                messages.error(request, f'Error: {ex}')

        return HttpResponseRedirect(request.path)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        if action == 'addclub':
            try:
                form = ClubForm(request.POST, request.FILES)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                newfile = form.cleaned_data['escudo']
                if newfile:
                    extension = newfile._name.split('.')
                    exte = extension[len(extension) - 1]
                    if newfile.size > 2194304:
                        raise NameError(u"El tamaño del archivo es mayor a 2 Mb.")
                    if not exte.lower() in ['png', 'jpg', 'jpeg']:
                        raise NameError(u"Solo se permite archivos de formato .png, .jpg, .jpeg")
                    newfile._name = generar_nombre_file(f'escudo', newfile._name)
                club = Club(nombre=form.cleaned_data['nombre'],
                            descripcion=form.cleaned_data['descripcion'],
                            tipoequipo=form.cleaned_data['tipoequipo'],
                            escudo=newfile)
                club.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'editclub':
            try:
                club = Club.objects.get(id=int(encrypt(request.POST['id'])))
                form = ClubForm(request.POST, request.FILES, instancia=club)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                newfile = form.cleaned_data['escudo']
                if newfile:
                    extension = newfile._name.split('.')
                    exte = extension[len(extension) - 1]
                    if newfile.size > 2194304:
                        raise NameError(u"El tamaño del archivo es mayor a 2 Mb.")
                    if not exte.lower() in ['png', 'jpg', 'jpeg']:
                        raise NameError(u"Solo se permite archivos de formato .png, .jpg, .jpeg")
                    newfile._name = generar_nombre_file(f'escudo', newfile._name)
                    club.escudo = newfile
                club.nombre = form.cleaned_data['nombre']
                club.descripcion = form.cleaned_data['descripcion']
                club.tipoequipo = form.cleaned_data['tipoequipo']
                club.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'delclub':
            try:
                pers = IntegranteClub.objects.get(id=int(encrypt(request.POST['id'])))
                pers.status = False
                pers.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})

        elif action == 'addintegrante':
            try:
                id_club = request.GET['id']
                form = IntegranteForm(request.POST, request.FILES)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                data = add_user_with_profile(request, form)
                tipojugador = form.cleaned_data['tipojugador'] if int(form.cleaned_data['rol']) == 1 else 0
                integrante = IntegranteClub(club_id=int(encrypt(id_club)),
                                            persona_id=data['id_persona'],
                                            rol=form.cleaned_data['rol'],
                                            tipojugador=tipojugador)
                integrante.save(request)
                return JsonResponse({"result": True, "url_redirect": f'{request.path}?action=integrantes&id={id_club}'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'editintegrante':
            try:
                integrante = IntegranteClub.objects.get(id=int(encrypt(request.POST['id'])))
                form = IntegranteForm(request.POST, request.FILES, instancia=integrante.persona)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                data = edit_persona_with_profile(request, form, 0, integrante.persona.id)
                tipojugador = form.cleaned_data['tipojugador'] if int(form.cleaned_data['rol']) == 1 else 0
                integrante.tipojugador = tipojugador
                integrante.rol = form.cleaned_data['rol']
                integrante.save(request)
                return JsonResponse({"result": True, "url_redirect": f'{request.path}?action=integrantes&id={encrypt(integrante.club.id)}'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'delintegrante':
            try:
                pers = IntegranteClub.objects.get(id=int(encrypt(request.POST['id'])))
                pers.status = False
                pers.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})

        elif action == 'addpartido':
            try:
                form = PartidoForm(request.POST)
                idtorneo = int(encrypt(request.POST['idp']))
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                partido = Partido(torneo_id=idtorneo,
                                  clublocal=form.cleaned_data['clublocal'],
                                  clubvisitante=form.cleaned_data['clubvisitante'],
                                  tipopartido=form.cleaned_data['tipopartido'],
                                  tipopartidofase=form.cleaned_data['tipopartidofase'],
                                  fecha=datetime.combine(form.cleaned_data['fecha'], form.cleaned_data['hora']))
                partido.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'editpartido':
            try:
                instancia = Partido.objects.get(id=int(encrypt(request.POST['id'])))
                form = PartidoForm(request.POST, instancia=instancia)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                instancia.clublocal = form.cleaned_data['clublocal']
                instancia.clubvisitante = form.cleaned_data['clubvisitante']
                instancia.tipopartido = form.cleaned_data['tipopartido']
                instancia.tipopartidofase = form.cleaned_data['tipopartidofase']
                instancia.fecha = datetime.combine(form.cleaned_data['fecha'], form.cleaned_data['hora'])
                instancia.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'registrargoles':
            try:
                id = int(encrypt(request.POST['id']))
                instancia = Partido.objects.get(id=id)
                instancia.goleslocal = request.POST['goleslocal']
                instancia.golesvisitante = request.POST['golesvisitante']
                instancia.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'registrartarjeta':
            try:
                id = int(encrypt(request.POST['id']))
                partido = Partido.objects.get(id=id)
                form = TarjetaForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                instancia = TarjetaPartido(partido=partido,
                                           club=form.cleaned_data['club'],
                                           tipotarjeta=form.cleaned_data['tipotarjeta'],
                                           tiempo=form.cleaned_data['tiempo'],
                                           minuto=form.cleaned_data['minuto'],
                                           valor=form.cleaned_data['tipotarjeta'].valor,
                                           integrante=form.cleaned_data['integrante'])
                instancia.save(request)
                # integrante=form.cleaned_data['integrante']
                # if integrante:
                #     if form.cleaned_data['tipotarjeta'].nombre.lower() in ['roja','rojas','rojo']:
                #         integrante.suspendido=True
                #         integrante.save(request)
                    
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'registrargol':
            try:
                id = int(encrypt(request.POST['id']))
                partido = Partido.objects.get(id=id)
                form = GolForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                instancia = GolPartido(partido=partido,
                                       club=form.cleaned_data['club'],
                                       tiempo=form.cleaned_data['tiempo'],
                                       minuto=form.cleaned_data['minuto'],
                                       integrante=form.cleaned_data['integrante'])
                instancia.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'finalizar':
            try:
                id = int(encrypt(request.POST['id']))
                partido = Partido.objects.get(id=id)
                partido.estado = 2
                partido.save(request)
                club_gana, club_pierde = partido.resultado_gana()
                resultado_local = partido.resultadopartido_set.filter(club=partido.clublocal, status=True).first()
                resultado = partido.resultadopartido_set.filter(club=partido.clubvisitante, status=True).first()

                if not club_gana:
                    if not resultado_local:
                        resultado_local = ResultadoPartido(partido=partido,
                                                           club=partido.clublocal,
                                                           empato=True, puntos=1)
                        resultado_local.save(request)
                    else:
                        resultado_local.empato = True
                        resultado_local.gano = False
                        resultado_local.puntos = 1
                        resultado_local.save(request)

                    if not resultado:
                        resultado = ResultadoPartido(partido=partido, club=partido.clubvisitante, empato=True, puntos=1)
                        resultado.save(request)
                    else:
                        resultado.empato = True
                        resultado.gano = False
                        resultado.puntos = 1
                        resultado.save(request)
                else:
                    resultado_gana = partido.resultadopartido_set.filter(club=club_gana, status=True).first()
                    resultado_pierde = partido.resultadopartido_set.filter(club=club_pierde, status=True).first()
                    if not resultado_gana:
                        resultado_gana = ResultadoPartido(partido=partido, club=club_gana, gano=True, puntos=3)
                        resultado_gana.save(request)
                    else:
                        resultado_gana.empato = False
                        resultado_gana.gano = True
                        resultado_gana.puntos = 3
                        resultado_gana.save(request)

                    if not resultado_pierde:
                        resultado_pierde = ResultadoPartido(partido=partido, club=club_pierde, puntos=0)
                        resultado_pierde.save(request)
                    else:
                        resultado_pierde.empato = False
                        resultado_pierde.gano = False
                        resultado_pierde.puntos = 0
                        resultado_pierde.save(request)
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'delpartido':
            try:
                pers = Partido.objects.get(id=int(encrypt(request.POST['id'])))
                pers.status = False
                pers.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})

        elif action == 'addtorneo':
            try:
                form = TorneoForm(request.POST)
                tipos = request.POST.getlist('tipo')
                equipos = request.POST.getlist('equipos')
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})

                instancia = Torneo(nombre=form.cleaned_data['nombre'],
                                   inicio=form.cleaned_data['inicio'],
                                   fin=form.cleaned_data['fin'],
                                   generotorneo=form.cleaned_data['generotorneo'])
                instancia.save(request)
                for tipo in tipos:
                    instancia.tipopartidos.add(int(tipo))
                for equipo in equipos:
                    instancia.equipos.add(int(equipo))

                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'edittorneo':
            try:
                tipos = request.POST.getlist('tipo')
                equipos = request.POST.getlist('equipos')
                torneo = Torneo.objects.get(id=int(encrypt(request.POST['id'])))
                form = TorneoForm(request.POST, instancia=torneo)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                torneo.nombre = form.cleaned_data['nombre']
                torneo.inicio = form.cleaned_data['inicio']
                torneo.fin = form.cleaned_data['fin']
                torneo.generotorneo = form.cleaned_data['generotorneo']
                torneo.save(request)
                torneo.tipopartidos.clear()
                for tipo in tipos:
                    torneo.tipopartidos.add(int(tipo))

                torneo.equipos.clear()
                for equipo in equipos:
                    torneo.equipos.add(int(equipo))
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'deltorneo':
            try:
                pers = Torneo.objects.get(id=int(encrypt(request.POST['id'])))
                pers.status = False
                pers.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})

        elif action == 'delgol':
            try:
                instancia = GolPartido.objects.get(id=int(encrypt(request.POST['id'])))
                instancia.status = False
                instancia.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})

        elif action == 'deltarjeta':
            try:
                instancia = TarjetaPartido.objects.get(id=int(encrypt(request.POST['id'])))
                instancia.status = False
                instancia.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})
        
        elif action == 'notificarpago':
            try:
                context={}
                instancia = Club.objects.get(id=int(encrypt(request.POST['id'])))
                torneo = Torneo.objects.get(id=int(encrypt(request.POST['args'])))
                director = instancia.total_integrantes().filter(rol=2).first()
                tarjetas=instancia.tarjetas_pagar(torneo)
                if director:
                    context['director'] = director.persona
                    context['equipo'] = instancia
                    context['rubro'] = tarjetas
                    send_email('Pago de rubros por tarjetas',
                        'Se le concedio los permisos para proceder con la creación del usuario en la plataforma',
                        director.persona.email,
                        context,
                        'correo_pago_individual.html')
                messages.success(request, 'Se notifico exitosamente el pago de rubros')
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})
        
        elif action == 'notificarpagos':
            try:
                context={}
                torneo = Torneo.objects.get(id=int(encrypt(request.POST['id'])))
                equipos = torneo.equipos.all()
                for instancia in equipos:
                    director = instancia.total_integrantes().filter(rol=2).first()
                    tarjetas=instancia.tarjetas_pagar(torneo)
                    if director and tarjetas:
                        context['director'] = director.persona
                        context['equipo'] = instancia
                        context['rubro'] = tarjetas
                        send_email('Pago de rubros por tarjetas', '',
                            director.persona.email,
                            context,
                            'correo_pago_individual.html')
                messages.success(request, 'Se notifico exitosamente el pago de rubros')
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})
        
        elif action == 'validarpagos':
            try:
                context={}
                tarjetas = request.POST.getlist('tarjetas')
                estado=int(request.POST['estado'] )
                if not tarjetas:
                    return JsonResponse({"result": False, "mensaje": f'Sin tarjetas disponibles para pagos'})  
                pago = PagoRubroTarjeta.objects.get(id=int(encrypt(request.POST['id'])))
                pago.estado = estado
                pago.observacion = request.POST['observacion']
                pago.save(request)
                pago.tarjetas.clear()
                if estado==2:
                    tarjetas=TarjetaPartido.objects.filter(id__in=tarjetas)
                    for tarjeta in tarjetas:
                        pago.tarjetas.add(tarjeta)
                        tarjeta.pagado=True
                        tarjeta.save()
                director = pago.equipo.total_integrantes().filter(rol=2).first()
                context['director'] = director.persona
                context['equipo'] = pago.equipo
                context['observacion'] = pago.observacion
                context['estado'] = estado = pago.get_estado_display()
                send_email(f'Validación de comprobante ({estado})', '',
                    director.persona.email,
                    context,
                    'correo_validacion.html')
                messages.success(request, 'Se valido y notifico exitosamente')
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})  
        
        return JsonResponse({"result": False, "mensaje": u"Solicitud Incorrecta."})
