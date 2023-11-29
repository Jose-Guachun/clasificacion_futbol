from django.contrib.auth.models import User
from users.models import Persona
from django.db import transaction

from core.funciones import generar_username, generar_password

def cargar_inputs(form):
    context = {}
    context['nombres'] = form.cleaned_data['nombres']
    context['apellido1'] = form.cleaned_data['apellido1']
    context['apellido2'] = form.cleaned_data['apellido2']
    context['cedula'] = form.cleaned_data['cedula'] if 'cedula' in form.cleaned_data else ''
    context['pasaporte'] = form.cleaned_data['pasaporte'] if 'pasaporte' in form.cleaned_data else ''
    context['email'] = form.cleaned_data['email']
    context['celular'] = form.cleaned_data['celular'] if 'celular' in form.cleaned_data else ''
    context['telefono'] = form.cleaned_data['telefono'] if 'telefono' in form.cleaned_data else ''
    context['sexo'] = form.cleaned_data['sexo'] if 'sexo' in form.cleaned_data else None
    context['nacionalidad'] = form.cleaned_data['nacionalidad'] if 'nacionalidad' in form.cleaned_data else None
    context['fecha_nacimiento'] = form.cleaned_data['fecha_nacimiento'] if 'fecha_nacimiento' in form.cleaned_data else None
    context['tipoprofesor'] = form.cleaned_data['tipoprofesor'] if 'tipoprofesor' in form.cleaned_data else None
    context['fechaingreso'] = form.cleaned_data['fechaingreso'] if 'fechaingreso' in form.cleaned_data else None
    context['activo'] = form.cleaned_data['activo'] if 'activo' in form.cleaned_data else None
    return context

def add_user_with_profile(request, form, tipoperfil, password=None, persona=None):
    try:
        context = {}
        data=cargar_inputs(form)
        username=generar_username(data['nombres'], data['apellido1'], data['apellido2'])
        password=generar_password(data['cedula'], data['apellido1'],data['apellido2']) if not password else password
        user=User(first_name=data['nombres'], last_name=data['apellido1'], email=data['email'], username=username)
        user.set_password(password)
        user.save(request)
        persona=Persona(usuario=user,
                        nombres=data['nombres'],
                        apellido1=data['apellido1'],
                        apellido2=data['apellido2'],
                        cedula=data['cedula'],
                        pasaporte=data['pasaporte'],
                        email=data['email'],
                        celular=data['celular'],
                        telefono=data['telefono'],
                        sexo=data['sexo'],
                        fecha_nacimiento=data['fecha_nacimiento'],
                        tipoperfil=tipoperfil,
                        nacionalidad=data['nacionalidad'])
        persona.save(request)
        context['id_persona'] = persona.id
        # if tipoperfil == 'docente':
        #     profesor=Profesor(persona=persona,tipoprofesor=data['tipoprofesor'], fechaingreso=data['fechaingreso'])
        #     if not data['activo'] is None:
        #         profesor.activo = data['activo']
        #     profesor.save(request)
        #     perfil=PerfilUsuario(profesor=profesor, persona=persona, perfilprincipal=True)
        #     perfil.save(request)
        #     context['id_profesor']=profesor.id
        # elif tipoperfil == 'administrativo':
        #     administrativo = Administrativo(persona=persona, fechaingreso=data['fechaingreso'])
        #     if not data['activo'] is None:
        #         administrativo.activo = data['activo']
        #     administrativo.save(request)
        #     perfil = PerfilUsuario(administrativo=administrativo, persona=persona)
        #     perfil.save(request)
        #     context['id_administrativo']=administrativo.id
        # elif tipoperfil == 'estudiante':
        #     estudiante = Estudiante(persona=persona)
        #     estudiante.save(request)
        #     perfil = PerfilUsuario(estudiante=estudiante, persona=persona)
        #     perfil.save(request)
        #     context['id_estudiante']=estudiante.id
        # context['id_perfil']=perfil.id
        return context
    except Exception as ex:
        transaction.set_rollback(True)
        raise NameError(str(ex))

def edit_persona_with_profile(request, form, tipoperfil, id_persona):
    context={}
    data = cargar_inputs(form)
    persona=Persona.objects.get(id=id_persona)
    persona.nombres=data['nombres']
    persona.apellido1=data['apellido1']
    persona.apellido2=data['apellido2']
    if not form.instancia.cedula:
        persona.cedula=data['cedula']
    if not form.instancia.pasaporte:
        persona.pasaporte=data['pasaporte']
    # persona.email=data['email']
    persona.celular=data['celular']
    persona.telefono=data['telefono']
    persona.sexo=data['sexo']
    persona.fecha_nacimiento=data['fecha_nacimiento']
    persona.nacionalidad=data['nacionalidad']
    persona.save(request)
    context['id_persona'] = persona.id
    # if tipoperfil == 'docente':
    #     profesor=Profesor.objects.get(persona=persona, status=True)
    #     profesor.tipoprofesor = data['tipoprofesor']
    #     if data['fechaingreso']:
    #         profesor.fechaingreso = data['fechaingreso']
    #     if not data['activo'] is None:
    #         profesor.activo = data['activo']
    #     profesor.save(request)
    #     context['id_profesor']=profesor.id
    # elif tipoperfil == 'administrativo':
    #     administrativo = Administrativo.objects.get(persona=persona, status=True)
    #     if data['fechaingreso']:
    #         administrativo.fechaingreso=data['fechaingreso']
    #     if not data['activo'] is None:
    #         administrativo.activo = data['activo']
    #     administrativo.save(request)
    #     context['id_administrativo']=administrativo.id
    # elif tipoperfil == 'estudiante':
    #     estudiante = Estudiante.objects.get(persona=persona, status=True)
    #     estudiante.save(request)
    #     context['id_estudiante']=estudiante.id
    return context

def gestionarusuario(request, form, object):
    try:
        #perfil_ = object.perfilusuario_set.get(status=True)
        #perfil_.activo = form.cleaned_data['perfilactivo']
        #perfil_.save(request)
        usuario_ = object.persona.usuario
        usuario_.is_active = form.cleaned_data['usuarioactivo']
        usuario_.save()
    except Exception as ex:
        raise NameError(str(ex))
