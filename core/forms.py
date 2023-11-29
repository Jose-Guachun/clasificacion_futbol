import random
from django import forms
from django.db import models
from django.db.models import Q
from django.forms.widgets import DateTimeBaseInput
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User
from users.models import Persona
from core.validators import v_cedulaform, v_sololetrasform, v_solonumerosform

def deshabilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True

def habilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = False

def campo_solo_lectura(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True

class CustomDateInput(DateTimeBaseInput):
    def format_value(self, value):
        return str(value or '')

class FormBase(forms.Form):

    def __init__(self, *args, **kwargs):
        self.ver = kwargs.pop('ver') if 'ver' in kwargs else False
        self.editando = 'instance' in kwargs
        no_requeridos = kwargs.pop('no_requeridos') if 'no_requeridos' in kwargs else []
        requeridos = kwargs.pop('requeridos') if 'requeridos' in kwargs else []
        if self.editando:
            self.instancia = kwargs['instance']
        super(FormBase, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages = {'required': f'Este campo es obligatorio'}
        for nr in no_requeridos:
            self.fields[nr].required = False
        for r in requeridos:
            self.fields[r].required = True
        for k, v in self.fields.items():
            field = self.fields[k]
            if isinstance(field, forms.TimeField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'time'})
                self.fields[k].widget.attrs = attrs_
                self.fields[k].widget.attrs['class'] = "form-control"
            if isinstance(field, forms.DateField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'date'})
                self.fields[k].widget.attrs = attrs_
                self.fields[k].widget.attrs['class'] = "form-control"
                # self.fields[k].input_formats = ['%d/%m/%Y']
            elif isinstance(field, forms.BooleanField):
                if 'switch' in self.fields[k].widget.attrs:
                    if 'class' in self.fields[k].widget.attrs :
                        self.fields[k].widget.attrs['class'] += " form-check-input"
                    else:
                        self.fields[k].widget.attrs['class'] = "form-check-input"
            elif isinstance(field, forms.ChoiceField) or isinstance(field, forms.ModelChoiceField) and self.fields[k].widget.input_type == 'select':
                if not 'select2' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['placeholder'] = f'Elige una opción'
                    if 'class' in self.fields[k].widget.attrs:
                        self.fields[k].widget.attrs['class'] += " form-control selectpicker"
                    else:
                        self.fields[k].widget.attrs['class'] = "form-control selectpicker"
            else:
                label=self.fields[k].label.lower()
                if 'class' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['class'] += " form-control"
                else:
                    self.fields[k].widget.attrs['class'] = "form-control"
            if not 'col' in self.fields[k].widget.attrs:
                self.fields[k].widget.attrs['col'] = "12"
            if self.fields[k].required and self.fields[k].label:
                self.fields[k].label = mark_safe(self.fields[k].label + '<span style="color:red;margin-left:2px;"><strong>*</strong></span>')
            self.fields[k].widget.attrs['data-nameinput'] = k
            if self.ver:
                self.fields[k].widget.attrs['readonly'] = "readonly"

class FormBaseUser(forms.Form):

    def __init__(self, *args, **kwargs):
        self.ver = kwargs.pop('ver') if 'ver' in kwargs else False
        self.instancia = kwargs.pop('instancia', None)
        no_requeridos = kwargs.pop('no_requeridos') if 'no_requeridos' in kwargs else []
        requeridos = kwargs.pop('requeridos') if 'requeridos' in kwargs else []
        super(FormBaseUser, self).__init__(*args, **kwargs)
        if 'nacionalidad' in self.fields:
            self.fields['nacionalidad'].label_from_instance = lambda obj: obj.nacionalidad.capitalize()
        for field in self.fields:
            self.fields[field].error_messages = {'required': f'Este campo es obligatorio'}
        for nr in no_requeridos:
            self.fields[nr].required = False
        for r in requeridos:
            self.fields[r].required = True
        for k, v in self.fields.items():
            field = self.fields[k]
            if isinstance(field, forms.TimeField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'time'})
                self.fields[k].widget.attrs = attrs_
                self.fields[k].widget.attrs['class'] = "form-control"
            if isinstance(field, forms.DateField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'date'})
                self.fields[k].widget.attrs = attrs_
                self.fields[k].widget.attrs['class'] = "form-control"
                # self.fields[k].input_formats = ['%d/%m/%Y']
            elif isinstance(field, forms.BooleanField):
                if 'switch' in self.fields[k].widget.attrs:
                    if 'class' in self.fields[k].widget.attrs :
                        self.fields[k].widget.attrs['class'] += " form-check-input"
                    else:
                        self.fields[k].widget.attrs['class'] = "form-check-input"
            elif isinstance(field, forms.ChoiceField) or isinstance(field, forms.ModelChoiceField) and self.fields[k].widget.input_type == 'select':
                if not 'select2' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['placeholder'] = f'Elige una opción'
                    if 'class' in self.fields[k].widget.attrs:
                        self.fields[k].widget.attrs['class'] += " form-control selectpicker"
                    else:
                        self.fields[k].widget.attrs['class'] = "form-control selectpicker"
            else:
                label=self.fields[k].label.lower()
                if 'class' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['class'] += " form-control"
                else:
                    self.fields[k].widget.attrs['class'] = "form-control"
            if not 'col' in self.fields[k].widget.attrs:
                self.fields[k].widget.attrs['col'] = "12"
            if self.fields[k].required and self.fields[k].label:
                self.fields[k].label = mark_safe(self.fields[k].label + '<span style="color:red;margin-left:2px;"><strong>*</strong></span>')
            self.fields[k].widget.attrs['data-nameinput'] = k
            if self.ver:
                self.fields[k].widget.attrs['readonly'] = "readonly"

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['nombres']=nombres = cleaned_data.get('nombres').upper()
        cleaned_data['apellido1']=apellido1 = cleaned_data.get('apellido1').upper()
        cleaned_data['apellido2']=apellido2 = cleaned_data.get('apellido2').upper()
        cleaned_data['email']=email=cleaned_data.get('email').lower()
        pasaporte = cleaned_data.get('pasaporte')
        cedula=cleaned_data.get('cedula')
        telefono=cleaned_data.get('telefono')
        celular=cleaned_data.get('celular')
        nacionalidad = cleaned_data.get('nacionalidad')

        if not pasaporte and not cedula:
            self.add_error('cedula','Llene por lo menos uno de los dos campos')
            self.add_error('pasaporte','Llene por lo menos uno de los dos campos')

        #Validaciones de campos
        v_sololetrasform(self,nombres,'nombres')
        v_sololetrasform(self,apellido1,'apellido1')
        v_sololetrasform(self,apellido2,'apellido2')
        if cedula:
            v_cedulaform(self, cedula,'cedula')
        if pasaporte:
            v_solonumerosform(self, pasaporte, 'pasaporte')
        if telefono:
            v_solonumerosform(self,telefono,'telefono')
        if telefono:
            v_solonumerosform(self, celular, 'celular')
        # if nacionalidad:
        #     v_sololetrasform(self,nacionalidad,'nacionalidad')
        #     cleaned_data['nacionalidad'] = nacionalidad.title()

        #Comprobar existencia con datos ingresados
        if not self.instancia and User.objects.filter(email=email).exists():
            self.add_error('email','El email ingresado ya esta en uso.')
        if cedula and Persona.objects.filter(cedula=cedula, status=True).exists():
            mensaje='La cédula ingresada ya esta en uso.'
            if self.instancia:
                cedula_actual = getattr(self.instancia, 'cedula', None)
                if not cedula == cedula_actual:
                    self.add_error('cedula',mensaje)
            else:
                self.add_error('cedula',mensaje)
        if pasaporte and Persona.objects.filter(pasaporte=pasaporte, status=True).exists():
            mensaje='El pasaporte ingresado ya esta en uso.'
            if self.instancia:
                pasaporte_actual=getattr(self.instancia,'pasaporte', None)
                if not pasaporte == pasaporte_actual:
                    self.add_error('pasaporte',mensaje)
            else:
                self.add_error('pasaporte', mensaje)
        return cleaned_data
