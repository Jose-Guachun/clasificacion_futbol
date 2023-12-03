from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.core import validators
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
#models
from core.forms import FormBase, FormBaseUser, deshabilitar_campo
from core.validators import SoloLetras
from users.models import SEXO, Pais, PERFIL_USUARIO

class ClubForm(FormBase):
    nombre=forms.CharField(label="Nombre del club",
                           required=True,
                           widget=forms.TextInput(attrs={'col':'12', 'icon':'fa-regular fa-futbol', 'placeholder': 'Describa el nombre del club'}))
    descripcion=forms.CharField(label="Descripción del club",
                                required=False,
                                widget=forms.Textarea(attrs={'col':'12', 'icon':'fa-regular fa-commenting','placeholder': 'Describa el club a crear'}))
    escudo = forms.ImageField(label="Escudo", required=False, widget=forms.FileInput(attrs={'icon':'fa-regular fa-image'}))
