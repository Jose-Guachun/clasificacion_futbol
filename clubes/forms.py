from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.core import validators
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# models
from clubes.models import TIPO_ROL, TIPO_JUGADOR, TIPO_CLUB, Club, TipoPartido, TipoPartidoFase, IntegranteClub, TipoTarjeta, Partido, TIEMPOS
from core.forms import FormBase, FormBaseUser, deshabilitar_campo, CustomTimeInput
from core.validators import SoloLetras
from users.models import SEXO, Pais, PERFIL_USUARIO, Provincia, Ciudad


class ClubForm(FormBase):
    nombre = forms.CharField(label="Nombre del club",
                             required=True,
                             widget=forms.TextInput(attrs={'col': '12', 'icon': 'fa-regular fa-futbol', 'placeholder': 'Describa el nombre del club'}))
    descripcion = forms.CharField(label="Descripción del club",
                                  required=False,
                                  widget=forms.Textarea(attrs={'col': '12', 'rows': '3', 'icon': 'fa-regular fa-commenting', 'placeholder': 'Describa el club a crear'}))
    tipoequipo = forms.ChoiceField(label=u"Tipo de equipo", required=True,
                                   choices=TIPO_CLUB,
                                   widget=forms.Select(attrs={'col': '12'}))
    escudo = forms.ImageField(label="Escudo", required=False, widget=forms.FileInput(attrs={'icon': 'fa-regular fa-image'}))


class IntegranteForm(FormBaseUser):
    nombres = forms.CharField(label=u'Nombres', max_length=100, required=True,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese los nombres del integrante', 'class': 'soloLetrasET'}))
    apellido1 = forms.CharField(label=u"Primer apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el primer apellido del integrante', 'class': 'soloLetrasET'}))
    apellido2 = forms.CharField(label=u"Segundo apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el segundo apellido del integrante', 'class': 'soloLetrasET'}))
    cedula = forms.CharField(label=u"Cédula", max_length=10, required=False,
                             widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese la cédula del integrante', 'class': 'soloNumeros'}))
    fecha_nacimiento = forms.DateField(label=u'Fecha nacimiento', required=True,
                                       widget=forms.DateTimeInput(attrs={'col': '6'}))
    pasaporte = forms.CharField(label=u"Pasaporte", max_length=13, required=False,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el pasaporte del integrante'}))
    celular = forms.CharField(label=u"Teléfono celular", max_length=50, required=True,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el teléfono celular del integrante', 'class': 'soloNumeros'}))
    telefono = forms.CharField(label=u"Teléfono", max_length=50, required=False,
                               widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el teléfono del integrante (opcional)', 'class': 'soloNumeros'}))
    email = forms.CharField(label=u"Correo electrónico", max_length=200, required=True,
                            widget=forms.EmailInput(attrs={'col': '6', 'placeholder': 'Ingrese el correo electrónico del integrante'}))
    sexo = forms.ChoiceField(label=u"Genero", required=True,
                             choices=SEXO,
                             widget=forms.Select(attrs={'col': '6'}))
    pais = forms.ModelChoiceField(label=u'Pais de residencia', required=False,
                                  queryset=Pais.objects.filter(status=True),
                                  widget=forms.Select(attrs={'col': '6', 'select2': True}))
    provincia = forms.ModelChoiceField(label=u'Provincia de residencia', required=False,
                                       queryset=Provincia.objects.filter(status=True),
                                       widget=forms.Select(attrs={'col': '6', 'select2': True}))
    ciudad = forms.ModelChoiceField(label=u'Ciudad de residencia', required=False,
                                    queryset=Ciudad.objects.filter(status=True),
                                    widget=forms.Select(attrs={'col': '6', 'select2': True}))
    nacionalidad = forms.ModelChoiceField(label=u'Nacionalidad', required=False,
                                          queryset=Pais.objects.filter(status=True),
                                          widget=forms.Select(attrs={'col': '6'}))
    direccion = forms.CharField(label=u"Dirección de domicilio", max_length=50, required=False,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese su dirección de calle principal'}))
    rol = forms.ChoiceField(label=u'Rol', required=True,
                            choices=TIPO_ROL,
                            widget=forms.Select(attrs={'col': '6'}))
    tipojugador = forms.ChoiceField(label=u'Tipo de jugador', required=False,
                                    choices=TIPO_JUGADOR[1:],
                                    widget=forms.Select(attrs={'col': '6'}))
    foto = forms.ImageField(label="Foto", required=False, widget=forms.FileInput(attrs={'col': '6'}))

    # def __init__(self, *args, **kwargs):
    #     super(IntegranteForm, self).__init__(*args, **kwargs)
    #     if not self.instancia:
    #         self.fields['provincia'].queryset = Provincia.objects.none()
    #         self.fields['ciudad'].queryset = Ciudad.objects.none()
    #     else:
    #         self.fields['pais'].initial = self.instancia.pais
    #         self.fields['provincia'].queryset = self.instancia.pais.provincias()
    #         self.fields['provincia'].initial = self.instancia.provincia
    #         self.fields['ciudad'].queryset = self.instancia.provincia.ciudades()
    #         self.fields['ciudad'].initial = self.instancia.ciudad

    def edit(self):
        deshabilitar_campo(self, 'email')
        if self.instancia:
            cedula = getattr(self.instancia, 'cedula', None)
            pasaporte = getattr(self.instancia, 'pasaporte', None)
            if cedula:
                deshabilitar_campo(self, 'cedula')
            if pasaporte:
                deshabilitar_campo(self, 'pasaporte')


class TorneoForm(FormBase):
    nombre = forms.CharField(label="Nombre del torneo",
                             required=True,
                             widget=forms.TextInput(attrs={'col': '12', 'icon': 'fas fa-trophy', 'placeholder': 'Describa el nombre del torneo'}))
    # tipopartidos = forms.ModelMultipleChoiceField(label=u"Partidos", required=False,
    #                                               queryset=TipoPartido.objects.filter(status=True),
    #                                               widget=forms.SelectMultiple(attrs={'col': '6'}))


class PartidoForm(FormBase):
    clublocal = forms.ModelChoiceField(label=u"Equipo local", required=True,
                                       queryset=Club.objects.filter(status=True),
                                       widget=forms.Select(attrs={'col': '6', 'class': 'select2'}))
    clubvisitante = forms.ModelChoiceField(label=u"Equipo visitante", required=True,
                                           queryset=Club.objects.filter(status=True),
                                           widget=forms.Select(attrs={'col': '6', 'class': 'select2'}))
    tipopartido = forms.ModelChoiceField(label=u"Tipo de partido", required=False,
                                         queryset=TipoPartido.objects.filter(status=True),
                                         widget=forms.Select(attrs={'col': '6'}))
    tipopartidofase = forms.ModelChoiceField(label=u"Fase", required=False,
                                             queryset=TipoPartidoFase.objects.filter(status=True),
                                             widget=forms.Select(attrs={'col': '6'}))
    fecha = forms.DateField(label=u'Fecha de encuentro', required=True, initial=datetime.now().date(),
                            widget=forms.DateTimeInput(attrs={'col': '6'}))
    hora = forms.TimeField(label=u'Hora de encuentro', required=True,
                           widget=forms.TimeInput(attrs={'col': '6'}))

    def clean(self):
        cleaned_data = super().clean()
        clublocal = cleaned_data.get('clublocal')
        clubvisitante = cleaned_data.get('clubvisitante')
        hoy = datetime.now()
        fecha = datetime.combine(cleaned_data.get('fecha'), cleaned_data.get('hora'))

        if clublocal == clubvisitante:
            self.add_error('clublocal', 'No se puede seleccionar el mismo equipo en ambos campos')
            self.add_error('clubvisitante', 'No se puede seleccionar el mismo equipo en ambos campos')
        # if fecha < hoy:
        #     self.add_error('fecha', 'No se puede seleccionar el mismo equipo en ambos campos')

        return cleaned_data


class TarjetaForm(FormBase):
    club = forms.ModelChoiceField(label=u"Equipo", required=True,
                                  queryset=Club.objects.filter(status=True),
                                  widget=forms.Select(attrs={'col': '12', 'class': 'select2'}))
    integrante = forms.ModelChoiceField(label=u"Jugador", required=False,
                                        queryset=IntegranteClub.objects.filter(status=True, rol=1),
                                        widget=forms.Select(attrs={'col': '12', 'class': 'select2'}))
    tipotarjeta = forms.ModelChoiceField(label=u"Tarjeta", required=True,
                                         queryset=TipoTarjeta.objects.filter(status=True),
                                         widget=forms.Select(attrs={'col': '6', 'class': 'select2'}))
    tiempo = forms.ChoiceField(label=u"Tiempo de partido", required=True,
                             choices=TIEMPOS,
                             widget=forms.Select(attrs={'col': '6'}))
    minuto = forms.IntegerField(label=u'Minuto de gol', required=True,
                                widget=forms.NumberInput(attrs={'col': '6', 'placeholder': '0'}))

class GolForm(FormBase):
    club = forms.ModelChoiceField(label=u"Equipo", required=True,
                                  queryset=Club.objects.filter(status=True),
                                  widget=forms.Select(attrs={'col': '12', 'class': 'select2'}))
    integrante = forms.ModelChoiceField(label=u"Jugador", required=False,
                                        queryset=IntegranteClub.objects.filter(status=True, rol=1),
                                        widget=forms.Select(attrs={'col': '12', 'class': 'select2'}))
    tiempo = forms.ChoiceField(label=u"Tiempo de partido", required=True,
                             choices=TIEMPOS,
                             widget=forms.Select(attrs={'col': '6'}))
    minuto = forms.IntegerField(label=u'Minuto de gol', required=True,
                                widget=forms.NumberInput(attrs={'col': '6', 'placeholder': '0'}))
