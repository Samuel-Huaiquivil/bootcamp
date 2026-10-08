"""Define el carrito de compra y sus reservas de cursos."""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return sum((item.precio for item in self.items.filter(reservado_hasta__gt=timezone.now())), Decimal('0'))


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    curso = models.ForeignKey('courses.Curso', on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    reservado_hasta = models.DateTimeField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['carrito', 'curso'], name='carrito_curso_unico')]
