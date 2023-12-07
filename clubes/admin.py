from django.contrib import admin
from core.models import ModeloBaseAdmin
from clubes.models import TipoPartido, Fase, TipoPartidoFase, TipoTarjeta


# Register your models here.


class TipoPartidoAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class FaseAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class TipoPartidoFaseAdmin(ModeloBaseAdmin):
    list_display = ('orden', 'tipopartido', 'fase')
    ordering = ('orden',)
    search_fields = ('orden', 'tipopartido', 'fase')

class TipoTarjetaAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(TipoPartido, TipoPartidoAdmin)
admin.site.register(Fase, FaseAdmin)
admin.site.register(TipoPartidoFase, TipoPartidoFaseAdmin)
admin.site.register(TipoTarjeta, TipoTarjetaAdmin)