from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Curso(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        PUBLICADO = 'publicado', 'Publicado'
        INICIADO = 'iniciado', 'Iniciado'
        FINALIZADO = 'finalizado', 'Finalizado'
        CANCELADO = 'cancelado', 'Cancelado'

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    objetivos = models.TextField(blank=True)
    cupos = models.PositiveIntegerField()
    fecha_inicio = models.DateTimeField()
    fecha_termino = models.DateTimeField()
    fecha_limite_inscripcion = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.BORRADOR)
    profesores = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='cursos_dictados', blank=True)
    version_cupos = models.PositiveIntegerField(default=0, editable=False)

    def clean(self):
        errores = {}
        if self.fecha_inicio and self.fecha_termino and self.fecha_termino <= self.fecha_inicio:
            errores['fecha_termino'] = 'Debe ser posterior al inicio.'
        if self.fecha_inicio and self.fecha_limite_inscripcion and self.fecha_limite_inscripcion > self.fecha_inicio:
            errores['fecha_limite_inscripcion'] = 'No puede ser posterior al inicio.'
        if self.precio is not None and self.precio < Decimal('0'):
            errores['precio'] = 'No puede ser negativo.'
        if errores:
            raise ValidationError(errores)

    def disponible_para_compra(self):
        ahora = timezone.now()
        return self.estado == self.Estado.PUBLICADO and ahora < self.fecha_inicio and ahora <= self.fecha_limite_inscripcion

    def __str__(self):
        return self.nombre
