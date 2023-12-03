import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from users.models.models_address import Pais, Provincia, Ciudad
from core.funciones import ruta_foto
from core.models import ModeloBase
from django.forms import model_to_dict

SEXO = (
    (1, u'Hombre'),
    (2, u'Mujer'),
)

PERFIL_USUARIO = (
    (0, 'Sin perfil'),
    (1, 'Administrador'),
    (2, 'Asistente'),
    (3, 'Registrador'),
)

class Persona(ModeloBase):
    usuario = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    perfil = models.IntegerField(choices=PERFIL_USUARIO, default=0, verbose_name=u'Tipo de usuario')
    nombres = models.CharField(default='', max_length=100, verbose_name=u'Nombre')
    apellido1 = models.CharField(default='', max_length=50, verbose_name=u"1er Apellido")
    apellido2 = models.CharField(default='', max_length=50, verbose_name=u"2do Apellido")
    cedula = models.CharField(default='', max_length=20, verbose_name=u"Cedula", blank=True, db_index=True)
    pasaporte = models.CharField(default='', max_length=20, blank=True, verbose_name=u"Pasaporte", db_index=True)
    fecha_nacimiento = models.DateField(verbose_name=u"Fecha de nacimiento o constitución", blank=True, null=True,)
    sexo = models.IntegerField(choices=SEXO, verbose_name=u'Sexo', blank=True, null=True)
    celular = models.CharField(default='', max_length=50, verbose_name=u"Telefono movil")
    telefono = models.CharField(default='', max_length=50, verbose_name=u"Telefono fijo")
    email = models.CharField(default='', max_length=200, verbose_name=u"Correo electrónico personal")
    nacionalidad = models.ForeignKey(Pais,blank=True, null=True,related_name='nacionalidades', on_delete=models.CASCADE, verbose_name="Nacionalidad que tiene el usuario")
    pais = models.ForeignKey(Pais, blank=True, null=True, related_name='+', verbose_name=u'País residencia', on_delete=models.CASCADE)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, related_name='+',verbose_name=u"Provincia de residencia", on_delete=models.CASCADE)
    ciudad = models.ForeignKey(Ciudad, blank=True, null=True, related_name='+', verbose_name=u"Ciudad de residencia", on_delete=models.CASCADE)
    direccion = models.CharField(default='', max_length=300, verbose_name=u"Calle principal")
    direccion2 = models.CharField(default='', max_length=300, verbose_name=u"Calle secundaria")
    num_direccion = models.CharField(default='', max_length=15, verbose_name=u"Numero")
    referencia = models.CharField(default='', max_length=100, verbose_name=u"Referencia")
    foto = models.ImageField(upload_to=ruta_foto, verbose_name=u'Foto',blank=True, null=True)

    def __str__(self):
        return self.nombres_completos_inverso()

    def nombres_completos_inverso(self):
        nombre_completo = f"{self.apellido1} {self.apellido2} {self.nombres}"
        return nombre_completo.title()

    def nombres_completos_lienal(self):
        nombre_completo = f"{self.nombres} {self.apellido1} {self.apellido2}"
        return nombre_completo.title()

    def nombres_simple(self):
        nombre_completo = self.nombres.split()[0].title()
        apellido1 = self.apellido1.title()
        return f"{nombre_completo} {apellido1}"

    def get_avatar_html_40px(self):
        if self.foto:
            return f'<div class="avatar avatar-md avatar-indicators avatar-online"><img alt="avatar" src="{self.foto.url}"class="rounded-circle"/></div>'
        else:
            siglas=self.nombres[0].upper()+self.apellido1[0].upper()
            return f'<div class="siglas-md mt-0 ml-1"> <span class="mt-0">{siglas}</span></div>'

    def get_avatar_img_md(self):
        if self.foto:
            return f'<img src="{self.foto.url}" class="rounded-circle avatar-md me-2"/>'
        else:
            siglas=self.nombres[0].upper()+self.apellido1[0].upper()
            return f'<div class="siglas-md mt-0 ml-1 me-2"> <span class="mt-0">{siglas}</span></div>'

    def get_avatar_img_sm(self):
        if self.foto:
            return f'<img src="{self.foto.url}" class="rounded-circle avatar-sm me-2"/>'
        else:
            siglas=self.nombres[0].upper()+self.apellido1[0].upper()
            return f'<div class="siglas-sm mt-0 ml-1 me-2"> <span class="mt-0">{siglas}</span></div>'

    def get_foto(self):
        return self.foto.url if self.foto else ''

    def mis_perfilesusuarios(self):
        return self.perfilusuario_set.filter(status=True,activo=True)

    def mi_perfil_principal(self):
        perfiles_p=self.mis_perfilesusuarios().filter(perfilprincipal=True)
        if perfiles_p.exists():
            return perfiles_p.first()
        return self.mis_perfilesusuarios().first()

    def to_dict(self):
        persona_dict=model_to_dict(self)
        for key, value in persona_dict.items():
            if isinstance(value, datetime.date):
                persona_dict[key] = value.strftime('%Y-%m-%d')
        return persona_dict

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Persona.objects.filter((Q(cedula=self.cedula) |
                                    Q(cedula=self.pasaporte) |
                                    Q(pasaporte=self.pasaporte) |
                                    Q(pasaporte=self.cedula) |
                                    Q(usuario__email=self.email) |
                                    Q(email=self.email)), status=True).exclude(pk=self.pk).exclude(pasaporte='',pasaporte__isnull=False).exclude(cedula__isnull=False, cedula='')
        if qs.exists():
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Persona"
        verbose_name_plural = u"Personas"
        ordering = ['apellido1', 'apellido2', 'nombres']
