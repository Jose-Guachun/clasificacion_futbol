from users.models import Persona, User
from django.db import transaction

from core.funciones import generar_username, generar_password, generar_nombre_file


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
    context['perfil'] = form.cleaned_data['perfil'] if 'perfil' in form.cleaned_data else 0
    context['direccion'] = form.cleaned_data['direccion'] if 'direccion' in form.cleaned_data else ''
    context['pais'] = form.cleaned_data['pais'] if 'pais' in form.cleaned_data else None
    context['provincia'] = form.cleaned_data['provincia'] if 'provincia' in form.cleaned_data else None
    context['ciudad'] = form.cleaned_data['ciudad'] if 'ciudad' in form.cleaned_data else None
    context['foto'] = form.cleaned_data['foto'] if 'foto' in form.cleaned_data else None
    return context


def add_user_with_profile(request, form, perfil=0, password=None, persona=None):
    try:
        context = {}
        data = cargar_inputs(form)
        perfil = perfil if perfil > 0 else data['perfil']
        is_active = int(perfil) > 0
        identificacion =data['cedula'] if data['cedula'] else data['pasaporte']
        username = generar_username(data['nombres'], data['apellido1'], data['apellido2'])
        password = generar_password(identificacion, data['apellido1'], data['apellido2']) if not password else password
        user = User(first_name=data['nombres'], last_name=data['apellido1'], email=data['email'], username=username, is_active=is_active)
        user.set_password(password)
        user.save(request)
        newfile = data['foto']
        if newfile:
            extension = newfile._name.split('.')
            exte = extension[len(extension) - 1]
            if newfile.size > 2194304:
                raise NameError(u"El tamaño del archivo es mayor a 2 Mb.")
            if not exte.lower() in ['png', 'jpg', 'jpeg']:
                raise NameError(u"Solo se permite archivos de formato .png, .jpg, .jpeg")
            newfile._name = generar_nombre_file(f'escudo', newfile._name)

        persona = Persona(usuario=user,
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
                          perfil=perfil,
                          direccion=data['direccion'],
                          pais=data['pais'],
                          ciudad=data['ciudad'],
                          provincia=data['provincia'],
                          foto=newfile,
                          nacionalidad=data['nacionalidad'])
        persona.save(request)
        context['id_persona'] = persona.id
        return context
    except Exception as ex:
        transaction.set_rollback(True)
        raise NameError(str(ex))


def edit_persona_with_profile(request, form, perfil=0, id_persona=None):
    context = {}
    data = cargar_inputs(form)
    persona = Persona.objects.get(id=id_persona)
    persona.nombres = data['nombres']
    persona.apellido1 = data['apellido1']
    persona.apellido2 = data['apellido2']
    if not form.instancia.cedula:
        persona.cedula = data['cedula']
    if not form.instancia.pasaporte:
        persona.pasaporte = data['pasaporte']
    # persona.email=data['email']
    persona.celular = data['celular']
    persona.telefono = data['telefono']
    persona.sexo = data['sexo']
    persona.fecha_nacimiento = data['fecha_nacimiento']
    persona.nacionalidad = data['nacionalidad']
    persona.perfil = int(perfil) if int(perfil) > 0 else data['perfil']
    persona.direccion = data['direccion']
    persona.pais = data['pais']
    persona.provincia = data['provincia']
    persona.ciudad = data['ciudad']
    newfile = data['foto']
    if newfile:
        extension = newfile._name.split('.')
        exte = extension[len(extension) - 1]
        if newfile.size > 2194304:
            raise NameError(u"El tamaño del archivo es mayor a 2 Mb.")
        if not exte.lower() in ['png', 'jpg', 'jpeg']:
            raise NameError(u"Solo se permite archivos de formato .png, .jpg, .jpeg")
        newfile._name = generar_nombre_file(f'foto', newfile._name)
        persona.foto=newfile
    persona.save(request)
    context['id_persona'] = persona.id
    return context


def gestionarusuario(form, object):
    try:
        usuario_ = object.persona.usuario
        usuario_.is_active = form.cleaned_data['usuarioactivo']
        usuario_.save()
    except Exception as ex:
        raise NameError(str(ex))
