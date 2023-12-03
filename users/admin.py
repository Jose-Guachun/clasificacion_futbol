from django.contrib import admin
from core.models import ModeloBaseAdmin
from users.models import Persona,Pais,Provincia,Ciudad
# Register your models here.
class PersonaAdmin(ModeloBaseAdmin):
    list_display = ('nombres',)
    ordering = ('nombres',)
    search_fields = ('nombres',)

class PaisAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class ProvinciaAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class CiudadAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)


admin.site.register(Persona, PersonaAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Ciudad, CiudadAdmin)