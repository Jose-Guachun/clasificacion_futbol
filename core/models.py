from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError

from clasificacion_futbol.settings import ADMINISTRADOR_ID
from django.contrib.auth.models import User

MANAGERS = (
    ('jguachuns', 'jose@gmail.com'),
)

class ModeloBase(models.Model):
    usuario_creacion = models.ForeignKey(
        User, related_name='+',
        blank=True, null=True,
        help_text='Usuario que creo el registro',
        on_delete=models.SET_NULL)
    usuario_modificacion = models.ForeignKey(
        User, related_name='+',
        blank=True, null=True,
        help_text='Usuario que modifico el registro',
        on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(
        'Fecha de creación',
        auto_now_add=True,
        help_text='Fecha y hora en que se creo el objeto'
    )
    fecha_modificacion = models.DateTimeField(
        'Fecha de modificacion',
        auto_now=True,
        help_text='Fecha y hora en el que se modifico el objeto'
    )
    status = models.BooleanField(
        'Estado del objeto',
        default=True,
        help_text='Estado del objeto'
    )

    def save(self, *args, **kwargs):
        self.validate_unique()
        models.Model.save(self)

    class Meta:
        """Meta option."""
        abstract = True
        get_latest_by = 'fecha_creacion'

class ModeloBaseAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.username not in [x[0] for x in MANAGERS]:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return request.user.username in [x[0] for x in MANAGERS]

    # def has_change_permission(self, request, obj=None):
    #     return True

    # def has_delete_permission(self, request, obj=None):
    #     return request.user.username in [x[0] for x in MANAGERS]

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("usuario_creacion", "fecha_creacion", "usuario_modificacion", "fecha_modificacion")
        form = super(ModeloBaseAdmin, self).get_form(request, obj, **kwargs)
        return form

    # def save_model(self, request, obj, form, change):
    #     if request.user.username not in [x[0] for x in MANAGERS]:
    #          raise Exception('Sin permiso a modificacion')
    #     else:
    #         obj.save(request)