"""Define órdenes, sus cursos asociados y el estado de los pagos."""

import uuid
from django.conf import settings
from django.db import models


class Orden(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADA = 'pagada', 'Pagada'
        FALLIDA = 'fallida', 'Fallida'
        CANCELADA = 'cancelada', 'Cancelada'
        REEMBOLSADA = 'reembolsada', 'Reembolsada'

    numero = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ordenes')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    creada_en = models.DateTimeField(auto_now_add=True)


class ItemOrden(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADO = 'pagado', 'Pagado'
        REEMBOLSADO = 'reembolsado', 'Reembolsado'

    orden = models.ForeignKey(Orden, on_delete=models.PROTECT, related_name='items')
    curso = models.ForeignKey('courses.Curso', on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    reservado_hasta = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['orden', 'curso'], name='orden_curso_unico')]


class Pago(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADO = 'aprobado', 'Aprobado'
        RECHAZADO = 'rechazado', 'Rechazado'
        REEMBOLSADO = 'reembolsado', 'Reembolsado'

    orden = models.OneToOneField(Orden, on_delete=models.PROTECT, related_name='pago')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    monto_reembolsado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actualizado_en = models.DateTimeField(auto_now=True)
