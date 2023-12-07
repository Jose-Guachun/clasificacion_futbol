from django.db import models
from django.utils.text import slugify

from core.models import ModeloBase

class Pais(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")
    nacionalidad = models.CharField(default='', max_length=100, verbose_name=u"Nacionalidad")
    codigonacionalidad = models.CharField(max_length=10, default="", verbose_name=u"Código nacionalidad")
    codigo = models.IntegerField(default=0, verbose_name=u"Código de pais")

    def __str__(self):
        return u'%s' % self.nombre

    def provincias(self):
        return self.provincia_set.filter(status=True)

    class Meta:
        verbose_name = u"País"
        verbose_name_plural = u"Paises"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def en_uso(self):
        return self.provincia_set.filter(status=True).values('id').exists()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.nacionalidad = self.nacionalidad.upper()
        self.codigonacionalidad = self.codigonacionalidad.upper()
        super(Pais, self).save(*args, **kwargs)

class Provincia(ModeloBase):
    pais = models.ForeignKey(Pais, blank=True, null=True, verbose_name=u'País', on_delete=models.CASCADE)
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")
    codigo = models.IntegerField(default=0, verbose_name=u"Código de provincia")

    def __str__(self):
        return u'%s' % self.nombre

    def ciudades(self):
        return self.ciudad_set.filter(status=True)

    class Meta:
        verbose_name = u"Provincia"
        verbose_name_plural = u"Provincias"
        ordering = ['nombre']
        unique_together = ('nombre', 'pais')

    def en_uso(self):
        return self.canton_set.values('id').all().exists()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Provincia, self).save(*args, **kwargs)

class Ciudad(ModeloBase):
    codigo = models.CharField(max_length=200, verbose_name='Código de ciudad', blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=200, verbose_name='Ciudad')
    lat = models.CharField(max_length=200, default='', blank=True, null=True, verbose_name='Latitud')
    long = models.CharField(max_length=200, default='', blank=True, null=True, verbose_name='Longitud')

    def __str__(self):
        return "{}".format(self.nombre)
        # return "{}, {}, {}".format(self.nombre, self.provincia.nombre, self.provincia.pais.nombre)

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ('nombre',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.nombre = self.nombre.upper()
        self.nombre_st = slugify(self.nombre).replace('-', ' ')
        super(Ciudad, self).save(force_insert, force_update, using)
