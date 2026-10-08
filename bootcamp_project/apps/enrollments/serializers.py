"""Serializa las inscripciones para las respuestas de la API."""

from rest_framework import serializers
from .models import Inscripcion


class InscripcionSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)

    class Meta:
        model = Inscripcion
        fields = ['id', 'estudiante', 'curso', 'curso_nombre', 'estado', 'creada_en']
