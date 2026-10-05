from django.conf import settings
from django.db import models


class Inscripcion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADA = 'confirmada', 'Confirmada'
        CANCELADA = 'cancelada', 'Cancelada'

    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='inscripciones')
    curso = models.ForeignKey('courses.Curso', on_delete=models.PROTECT, related_name='inscripciones')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.CONFIRMADA)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['estudiante', 'curso'], name='estudiante_curso_unico')]
