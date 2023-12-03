from django.db import models
from core.models import ModeloBase
from users.models import Persona

TIPO_ROL = (
    (1, 'Jugador'),
    (2, 'Director Técnico'),
    (3, 'Cuerpo Técnico'),
    (4, 'Gerente Deportivo'),
    (5, 'Presidente'),
    (6, 'Director Financiero'),
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

# Create your models here.
class Club(ModeloBase):
    nombre = models.CharField(default='', max_length=500, verbose_name=u"Nombre del club")
    descripcion = models.TextField(default='', verbose_name=u"descripción del club")
    escudo = models.ImageField(upload_to='club', verbose_name=u'Escudo del club', blank=True, null=True)
    
    def __str__(self):
        return u'%s' % self.nombre

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Club.objects.filter(nombre=self.nombre, status=True).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')   

    # def en_uso(self):
    #     return self.provincia_set.filter(status=True).values('id').exists()

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
        return f'{self.club}-{self.persona}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = IntegranteClub.objects.filter(status=True, club=self.club, persona=self.persona).exclude(pk=self.pk).exists()
        if qs:
            raise NameError('Ya existe un registro con los datos que intenta registrar.')   

    # def en_uso(self):
    #     return self.provincia_set.filter(status=True).values('id').exists()

    class Meta:
        verbose_name = u"Integrante del club"
        verbose_name_plural = u"Integrantes del club"
        ordering = ['persona']