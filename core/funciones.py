from django.core.paginator import Paginator
from django.db.models import Q
from unidecode import unidecode

from django.contrib.auth.models import User


def filtro_persona_generico(filtro, search):
    q = search.upper().strip()
    s = q.split(" ")
    if len(s) == 1:
        filtro = filtro & ((Q(persona__nombres__icontains=q) |
                            Q(persona__apellido1__icontains=q) |
                            Q(persona__cedula__icontains=q) |
                            Q(persona__apellido2__icontains=q) |
                            Q(persona__cedula__contains=q)))
    elif len(s) == 2:
        filtro = filtro & ((Q(persona__apellido1__contains=s[0]) & Q(persona__apellido2__contains=s[1])) |
                           (Q(persona__nombres__icontains=s[0]) & Q(persona__nombres__icontains=s[1])) |
                           (Q(persona__nombres__icontains=s[0]) & Q(persona__apellido1__contains=s[1])))
    else:
        filtro = filtro & ((Q(persona__nombres__contains=s[0]) & Q(persona__apellido1__contains=s[1]) & Q(persona__apellido2__contains=s[2])) |
                           (Q(persona__nombres__contains=s[0]) & Q(persona__nombres__contains=s[1]) & Q(persona__apellido1__contains=s[2])))
    return filtro

def filtro_persona_generico_principal(filtro, search):
    q = search.upper().strip()
    s = q.split(" ")
    if len(s) == 1:
        filtro = filtro & ((Q(nombres__icontains=q) |
                            Q(apellido1__icontains=q) |
                            Q(cedula__icontains=q) |
                            Q(apellido2__icontains=q) |
                            Q(cedula__contains=q)))
    elif len(s) == 2:
        filtro = filtro & ((Q(apellido1__contains=s[0]) & Q(apellido2__contains=s[1])) |
                           (Q(nombres__icontains=s[0]) & Q(nombres__icontains=s[1])) |
                           (Q(nombres__icontains=s[0]) & Q(apellido1__contains=s[1])))
    else:
        filtro = filtro & ((Q(nombres__contains=s[0]) & Q(apellido1__contains=s[1]) & Q(apellido2__contains=s[2])) |
                           (Q(nombres__contains=s[0]) & Q(nombres__contains=s[1]) & Q(apellido1__contains=s[2])))
    return filtro

def generar_username(nombres, apellido1, apellido2):
    username = nombres[0] + apellido1 + apellido2[0]
    if User.objects.filter(username=username.lower()).exists():
        for numero in range(1, 20):
            username += f'{numero}'
            if not User.objects.filter(username=username).exists():
                break
    return text_unnaccent(username)


def generar_password(cedula, apellido1, apellido2):
    return apellido1[0].upper() + cedula + apellido2[0].lower()


def text_unnaccent(texto):
    return unidecode(texto.strip()).lower()


def colorEstado(estado):
    if estado == 'planificado':
        return 'bg-primary'
    elif estado == 'en_curso':
        return 'bg-success'
    elif estado == 'finalizado':
        return 'bg-secondary'
    return 'badge bg-default'


def ruta_foto(instance, filename):
    # Guardar la imagen en MEDIA_ROOT/username/filename
    return '{0}/{1}/{2}'.format(instance.user.username, 'foto', filename)


class Paginacion(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, rango=5):
        super(Paginacion, self).__init__(object_list, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
        self.rango = rango
        self.paginas = []
        self.primera_pagina = False
        self.ultima_pagina = False

    def rangos_paginado(self, pagina):
        left = pagina - self.rango
        right = pagina + self.rango
        if left < 1:
            left = 1
        if right > self.num_pages:
            right = self.num_pages
        self.paginas = range(left, right + 1)
        self.primera_pagina = True if left > 1 else False
        self.ultima_pagina = True if right < self.num_pages else False
        self.ellipsis_izquierda = left - 1
        self.ellipsis_derecha = right + 1
