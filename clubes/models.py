from datetime import datetime

from django.db import models
from django.db.models import Sum, Value, Count
from django.db.models.functions import Coalesce

from core.models import ModeloBase
from users.models import Persona

TIPO_ROL = (
    (1, 'Jugador'),
    (2, 'Director Técnico'),
)
TIPO_JUGADOR = (
    (0, 'No es Jugador'),
    (1, 'Portero'),
    (2, 'Defensa'),
    (3, 'Centrocampista'),
    (4, 'Delantero'),
    (5, 'Suplente'),
    (6, 'Capitán'),
)

TIPO_CLUB = (
    (1, 'Hombres'),
    (2, 'Mujeres')
)
TIEMPOS = (
    (1, 'Primer Tiempo'),
    (2, 'Segundo Tiempo '),
    (3, 'Tiempo Extra Primer Tiempo'),
    (4, 'Tiempo Extra Primer Tiempo'),

)

ESTADO_PARTIDO = (
    (1, 'Planificado'),
    (2, 'Finalizado')
)
# Create your models here.
class Club(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre del club")
    descripcion = models.TextField(default='', verbose_name=u"descripción del club")
    tipoequipo = models.IntegerField(choices=TIPO_CLUB, default=1, verbose_name=u'Tipo de equipo')
    escudo = models.ImageField(upload_to='club', verbose_name=u'Escudo del club', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

    def club_in_torneo(self, idtorneo=None):
        if idtorneo:
            torneo = Torneo.objects.get(id=int(idtorneo))
            return self in torneo.equipos.all()
        return False

    def resultados_torneo(self, torneo):
        resultados = self.resultadopartido_set.filter(status=True, partido__torneo=torneo)
        tarjetas = self.tarjetapartido_set.filter(status=True, partido__torneo=torneo)
        context = {'total_partidos': len(resultados),
                   'total_puntos': resultados.aggregate(totalpuntos=Coalesce(Sum('puntos'), Value(0)))['totalpuntos'],
                   'total_tarjetas': len(tarjetas),
                   'tarjeta': tarjetas.values('tipotarjeta__nombre').annotate(conteo=Count('id')),
                   'total_pagar': tarjetas.aggregate(totalpagar=Coalesce(Sum('tipotarjeta__valor'), Value(0.00)))['totalpagar']
                   }
        return context

    def total_integrantes(self):
        return self.integranteclub_set.filter(status=True)

    def siglas(self):
        nombre = self.nombre.split(' ')
        if len(nombre) == 1:
            siglas = self.nombre[0].upper() + self.nombre[-1].upper()
        else:
            siglas = nombre[0][0].upper() + nombre[1][0].upper()
        return siglas

    def get_escudo_html_40px(self):
        if self.escudo:
            return f'<div class="avatar avatar-md avatar-indicators avatar-online"><img alt="avatar" src="{self.escudo.url}"class="rounded-circle"/></div>'
        else:
            return f'<div class="siglas-md mt-0 ml-1"> <span class="mt-0 bg-secondary">{self.siglas()}</span></div>'

    def get_escudo_img_md(self):
        if self.escudo:
            return f'<img src="{self.escudo.url}" class="rounded-circle avatar-md me-2"/>'
        else:
            return f'<div class="siglas-md mt-0 ml-1 me-2"> <span class="mt-0 bg-secondary">{self.siglas()}</span></div>'

    def get_escudo_img_sm(self):
        if self.escudo:
            return f'<img src="{self.escudo.url}" class="rounded-circle avatar-xs me-2"/>'
        else:
            return f'<img src="/static/images/escudo.png" class="avatar-xs me-2"/>'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Club.objects.filter(nombre=self.nombre, status=True).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    def resultado_partido(self, partido):
        resultado = self.resultadopartido_set.filter(status=True, partido=partido).first()
        return resultado

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Club, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Club"
        verbose_name_plural = u"Clubes"
        ordering = ['nombre']


class IntegranteClub(ModeloBase):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name=u"Club")
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name=u"Club")
    rol = models.IntegerField(choices=TIPO_ROL, default=1, verbose_name=u'Tipo de rol en el club')
    tipojugador = models.IntegerField(choices=TIPO_JUGADOR, default=0, verbose_name=u'Tipo de jugador en el club')

    def __str__(self):
        return f'{self.persona}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = IntegranteClub.objects.filter(status=True, club=self.club, persona=self.persona).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Integrante del club"
        verbose_name_plural = u"Integrantes del club"
        ordering = ['persona']


class Fase(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre de la fase")
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"descripción de la fase")

    def __str__(self):
        return f'{self.nombre}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Fase.objects.filter(status=True, nombre=self.nombre).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Fase"
        verbose_name_plural = u"Fases"
        ordering = ['nombre']


class TipoPartido(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre del partido")
    descripcion = models.TextField(default='', blank=True, null=True, verbose_name=u"descripción del partido")

    def __str__(self):
        return f'{self.nombre}'

    def tipomarcado(self, torneo=False):
        if torneo:
            return torneo.tipopartidos.filter(id=self.id).exists()
        return torneo

    def fases(self):
        return self.tipopartidofase_set.filter(status=True)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = TipoPartido.objects.filter(status=True, nombre=self.nombre).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Tipo Partido"
        verbose_name_plural = u"Topos Partidos"
        ordering = ['nombre']


class TipoPartidoFase(ModeloBase):
    tipopartido = models.ForeignKey(TipoPartido, on_delete=models.CASCADE, verbose_name=u"Partido", )
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, verbose_name=u"Fase", )
    puntos = models.IntegerField(default=3, verbose_name=u"Puntos por partido")
    orden = models.IntegerField(default=0, verbose_name=u"Orden")

    def __str__(self):
        return f'{self.tipopartido}-{self.fase}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = TipoPartidoFase.objects.filter(status=True, tipopartido=self.tipopartido, fase=self.fase).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Fase de Partido"
        verbose_name_plural = u"Fases de Partidos"
        ordering = ['orden']


class Torneo(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre del torneo")
    tipopartidos = models.ManyToManyField(TipoPartido, verbose_name="Tipos de partidos que se jugaran")
    generotorneo = models.IntegerField(choices=TIPO_CLUB, default=1, verbose_name="genero de participantes")
    equipos = models.ManyToManyField(Club, verbose_name='Equipos que participan en el torneo')

    def __str__(self):
        return f'{self.nombre}-{self.get_generotorneo_display()}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Torneo.objects.filter(status=True, nombre=self.nombre).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    def color_genero(self):
        if self.generotorneo == 2:
            return 'text-pink'
        else:
            return 'text-primary'

    def goleadores(self):
        goleadores = GolPartido.objects\
            .filter(status=True, partido__torneo=self, integrante__isnull=False)\
            .values('integrante',
                    'integrante__persona__nombres',
                    'club__nombre',
                    'integrante__persona__apellido1',
                    'integrante__persona__apellido2',
                    'integrante__persona__foto',
                    'integrante__persona__nacionalidad__nacionalidad') \
            .annotate(total_goles=Count('integrante'))\
            .order_by('-total_goles').distinct()
        return goleadores

    class Meta:
        verbose_name = u"Torneo"
        verbose_name_plural = u"Torneos"
        ordering = ['-fecha_creacion']


class Partido(ModeloBase):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"torneo")
    clublocal = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Club Local", related_name='clublocal')
    goleslocal = models.IntegerField(default=0, verbose_name=u'Cantidad de goles realizo el equipo local')
    clubvisitante = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Club Visitante", related_name='clubvisitante')
    golesvisitante = models.IntegerField(default=0, verbose_name=u'Cantidad de goles realizo el equipo visitante')
    tipopartido = models.ForeignKey(TipoPartido, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Partido Fase")
    tipopartidofase = models.ForeignKey(TipoPartidoFase, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Partido Fase")
    fecha = models.DateTimeField(blank=True, null=True, verbose_name='Fecha del partido')
    estado = models.IntegerField(default=1, choices=ESTADO_PARTIDO, verbose_name=u'Estado del Partido')

    def __str__(self):
        return f'{self.clublocal} VS {self.clubvisitante}'

    def goles_local(self):
        return len(self.golpartido_set.filter(status=True, club=self.clublocal))

    def goles_l(self):
        return self.golpartido_set.filter(status=True, club=self.clublocal)

    def goles_visitante(self):
        return len(self.golpartido_set.filter(status=True, club=self.clubvisitante))

    def goles_v(self):
        return self.golpartido_set.filter(status=True, club=self.clubvisitante)

    def t_tarjeta_local(self):
        return len(self.tarjetapartido_set.filter(status=True, club=self.clublocal))

    def tarjetas_local(self):
        return self.tarjetapartido_set.filter(status=True, club=self.clublocal)

    def t_tarjeta_visitante(self):
        return len(self.tarjetapartido_set.filter(status=True, club=self.clubvisitante))

    def tarjetas_visitante(self):
        return self.tarjetapartido_set.filter(status=True, club=self.clubvisitante)

    def estado_indentify(self):
        hoy = datetime.now()
        fecha = datetime.strptime(self.fecha.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        if fecha <= hoy and self.estado == 1:
            return 3, 'Jugando'
        return self.estado

    def esta_jugando(self):
        hoy = datetime.now()
        fecha = datetime.strptime(self.fecha.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        if fecha <= hoy and self.estado == 1:
            return True
        return False

    def get_estado(self):
        hoy = datetime.now()
        fecha = datetime.strptime(self.fecha.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        if fecha <= hoy and self.estado == 1:
            return f'<span class="badge bg-primary">Jugando</span>'
        elif self.estado == 2:
            return f'<span class="badge bg-success">{self.get_estado_display()}</span>'
        return f'<span class="badge bg-secondary">{self.get_estado_display()}</span>'

    def resultado_gana(self):
        goles_visitante = len(self.golpartido_set.filter(status=True, club=self.clubvisitante))
        goles_local = len(self.golpartido_set.filter(status=True, club=self.clublocal))
        if goles_visitante > goles_local:
            return self.clubvisitante, self.clublocal
        elif goles_visitante == goles_local:
            return None, None
        else:
            return self.clublocal, self.clubvisitante

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Partido.objects.filter(status=True, clublocal=self.clublocal, clubvisitante=self.clubvisitante, fecha=self.fecha).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Partido"
        verbose_name_plural = u"Partidos"
        ordering = ['-fecha']


class TipoTarjeta(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre de la tarjeta")
    valor = models.FloatField(default=0, blank=True, null=True, verbose_name=u"Valor de tarjeta")

    def __str__(self):
        return f'{self.nombre}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = TipoTarjeta.objects.filter(status=True, nombre=self.nombre).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Tipo de tarjeta"
        verbose_name_plural = u"Tipos de tarjetas"
        ordering = ['nombre']


class TarjetaPartido(ModeloBase):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Partido en el que recibe la tarjeta")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Club que recibe la tarjeta")
    integrante = models.ForeignKey(IntegranteClub, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Integrante que recibe la tarjeta")
    tipotarjeta = models.ForeignKey(TipoTarjeta, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Tarjeta otorgada")
    cantidad = models.IntegerField(default=1, verbose_name=u'Cantidad de tarjetas')
    minuto = models.IntegerField(default=0, verbose_name='Minutos en el que le dio la tarjeta')
    tiempo = models.IntegerField(default=0, choices=TIEMPOS, verbose_name=u'Tiempo en el que le marcaron tarjeta')

    def __str__(self):
        return f'{self.tarjeta} - {self.integrante}'

    class Meta:
        verbose_name = u"Tarjeta partido"
        verbose_name_plural = u"Tarjetas de partidos"
        ordering = ['-fecha_creacion']


class GolPartido(ModeloBase):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Partido en el que recibe la tarjeta")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Club que recibe la tarjeta")
    integrante = models.ForeignKey(IntegranteClub, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Integrante que recibe la tarjeta")
    cantidad = models.IntegerField(default=1, verbose_name=u'Cantidad de goles')
    tiempo = models.IntegerField(default=0, choices=TIEMPOS, verbose_name=u'Tiempo en el que metio el gol')
    minuto = models.IntegerField(default=0, verbose_name='Minutos en el que metio el gol')

    def __str__(self):
        return f'Gol - {self.get_tiempo_display}'

    class Meta:
        verbose_name = u"Gol partido"
        verbose_name_plural = u"Goles de partidos"
        ordering = ['-fecha_creacion']


class ResultadoPartido(ModeloBase):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Partido")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Equipo ")
    gano = models.BooleanField(default=False, verbose_name='Gano partido')
    empato = models.BooleanField(default=False, verbose_name='Empato partido')
    puntos = models.IntegerField(default=0, verbose_name='Puntos ganados')

    def __str__(self):
        return f'Resultados de {self.club}'

    class Meta:
        verbose_name = u"Resultado Partido"
        verbose_name_plural = u"Resultados Partidos"
        ordering = ['-fecha_creacion']
