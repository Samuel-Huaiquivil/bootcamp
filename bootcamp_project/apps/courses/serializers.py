from rest_framework import serializers
from .models import Curso


class CursoSerializer(serializers.ModelSerializer):
    profesores = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    cupos_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = ['id', 'nombre', 'descripcion', 'objetivos', 'cupos', 'cupos_disponibles',
                  'fecha_inicio', 'fecha_termino', 'fecha_limite_inscripcion', 'precio', 'estado', 'profesores']

    def get_cupos_disponibles(self, obj):
        from apps.orders.services import cupos_disponibles
        return cupos_disponibles(obj)

    def validate(self, attrs):
        from django.core.exceptions import ValidationError
        datos = {campo.name: getattr(self.instance, campo.name) for campo in Curso._meta.fields if self.instance and campo.name != 'id'}
        curso = Curso(**{**datos, **attrs})
        try:
            curso.clean()
        except ValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        if self.instance and 'cupos' in attrs:
            from apps.orders.services import cupos_disponibles
            ocupados = self.instance.cupos - cupos_disponibles(self.instance)
            if attrs['cupos'] < ocupados:
                raise serializers.ValidationError({'cupos': 'No puede ser menor que los cupos ocupados o reservados.'})
        return attrs
