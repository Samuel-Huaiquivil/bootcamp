"""Aplica las reglas para inscribir estudiantes en cursos."""

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.courses.models import Curso
from apps.orders.services import bloquear_curso, cupos_disponibles, validar_compra
from apps.users.models import Usuario
from .models import Inscripcion


@transaction.atomic
def inscribir_estudiante(estudiante, curso_id):
    if estudiante.rol != Usuario.Rol.ESTUDIANTE:
        raise ValidationError('El usuario debe ser estudiante.')
    curso = bloquear_curso(curso_id)
    validar_compra(estudiante, curso)
    if cupos_disponibles(curso) < 1:
        raise ValidationError('No quedan cupos disponibles.')
    inscripcion, _ = Inscripcion.objects.update_or_create(
        estudiante=estudiante,
        curso=curso,
        defaults={'estado': Inscripcion.Estado.CONFIRMADA},
    )
    return inscripcion
