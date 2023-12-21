import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from core.mail import send_email

from users.forms import UsuarioForm, UsuarioPermisoForm
from users.models import Persona
from users.models.models_profile import UsuariosAcceso
from users.templatetags.extra_tags import encrypt
from core.funciones import Paginacion, filtro_persona_generico, filtro_persona_generico_principal
from core.generic_save import add_user_with_profile, edit_persona_with_profile, gestionarusuario


class ViewSet(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action')
        context['persona'] = request.user.persona_set.get(status=True)
        context['viewactivo'] = 'usuarios'
        if action:
            if action == 'addusuario':
                try:
                    context['title'] = 'Adicionar usuario'
                    context['form'] = UsuarioForm()
                    template_name = 'usuarios/formularios/formadministrativo.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    messages.error(request, f'{ex}')

            if action == 'editusuario':
                try:
                    context['title'] = f'Editar usuario'
                    context['id'] = id = int(encrypt(request.GET['id']))
                    persona = Persona.objects.get(id=id)
                    context['form'] = form = UsuarioForm(instancia=persona, initial=model_to_dict(persona))
                    form.edit()
                    template_name = 'usuarios/formularios/formadministrativo.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    messages.error(request, f'{ex}')

            if action == 'addpermiso':
                try:
                    context['title'] = 'Adicionar permiso de registro'
                    context['form'] = UsuarioPermisoForm()
                    template = get_template('base_ajax_form_modal.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
                
            if action == 'editpermiso':
                try:
                    context['title'] = 'Editar permiso de registro'
                    usuarioacceso=UsuariosAcceso.objects.get(id=int(encrypt(request.GET['id'])))
                    context['form'] = UsuarioPermisoForm(initial=model_to_dict(usuarioacceso))
                    context['id'] = usuarioacceso.id
                    template = get_template('base_ajax_form_modal.html')
                    return JsonResponse({'result': True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
                
            if action == 'permisos':
                try:
                    context['title'] = 'Identificaciones permitidas para registro'
                    filtro, url_vars, search = Q(status=True), f'', request.GET.get('s')
                    if search:
                        context['s'] = search
                        url_vars += '&s=' + search
                        filtro = filtro & Q(cedula=search)|Q(email=search)

                    usuarios = UsuariosAcceso.objects.filter(filtro)
                    # PAGINADOR
                    paginator = Paginacion(usuarios, 10)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    template_name = 'usuarios/permisos.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    messages.error(request, f'Error: {ex}')
            
            messages.error(request, f'Solicitud incorrecta')
            return HttpResponseRedirect(request.path)
        else:
            try:
                context['title'] = 'Usuarios'
                filtro, url_vars, search = Q(status=True, perfil__gte=1), f'', request.GET.get('s')
                if search:
                    context['s'] = search
                    url_vars += '&s=' + search
                    filtro = filtro_persona_generico_principal(filtro, search)

                cursos = Persona.objects.filter(filtro)
                # PAGINADOR
                paginator = Paginacion(cursos, 10)
                page = int(request.GET.get('page', 1))
                paginator.rangos_paginado(page)
                context['paging'] = paging = paginator.get_page(page)
                context['listado'] = paging.object_list
                template_name = 'usuarios/view.html'
                return render(request, template_name, context)
            except Exception as ex:
                messages.error(request, f'Error: {ex}')

        return HttpResponseRedirect(request.path)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        if action == 'addusuario':
            try:
                form = UsuarioForm(request.POST, request.FILES)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                data = add_user_with_profile(request, form)
                return JsonResponse({"result": True, "url_redirect": request.path})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'editusuario':
            try:
                pers = Persona.objects.get(id=int(encrypt(request.POST['id'])))
                form = UsuarioForm(request.POST, request.FILES, instancia=pers)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                data = edit_persona_with_profile(request, form, 0, pers.id)
                return JsonResponse({"result": True, "url_redirect": request.path})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'delusuario':
            try:
                pers = Persona.objects.get(id=int(encrypt(request.POST['id'])))
                pers.status = False
                pers.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})

        
        elif action == 'addpermiso':
            try:
                form = UsuarioPermisoForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})

                instancia = UsuariosAcceso(cedula=form.cleaned_data['cedula'],
                                            email=form.cleaned_data['email'])
                instancia.save(request)
                send_email('Permiso asignado para creación de usuario',
                           'Se le concedio los permisos para proceder con la creación del usuario en la plataforma',
                           instancia.email,
                           instancia,
                           'correo_permiso.html')
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'editpermiso':
            try:
                instancia = UsuariosAcceso.objects.get(id=int(encrypt(request.POST['id'])))
                form = UsuarioPermisoForm(request.POST, instancia=instancia)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                instancia.cedula = form.cleaned_data['cedula']
                instancia.email = form.cleaned_data['email']
                instancia.save(request)
                send_email('Permiso asignado para creación de usuario',
                           'Se le concedio los permisos para proceder con la creación del usuario en la plataforma',
                           instancia.email,
                           instancia,
                           'correo_permiso.html')
                return JsonResponse({"result": True, })
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        elif action == 'delpermiso':
            try:
                instancia = UsuariosAcceso.objects.get(id=int(encrypt(request.POST['id'])))
                instancia.status = False
                instancia.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})
            
        elif action == 'activardosfactore':
            try:
                instancia = request.user.persona_set.get()
                instancia.dosfactores = not instancia.dosfactores
                instancia.save(request)
                if instancia.dosfactores:
                    messages.success(request, 'Se activo exitosamente la autenticación de dos factores')
                else:
                    messages.info(request, 'Se desactivo exitosamente la autenticación de dos factores')
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                return JsonResponse({"result": False, "mensaje": f'Error {ex}'})
        
        return JsonResponse({"result": False, "mensaje": u"Solicitud Incorrecta."})
