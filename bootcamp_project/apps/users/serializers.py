from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol']


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data, rol=Usuario.Rol.ESTUDIANTE)


class CrearUsuarioAdminSerializer(RegistroSerializer):
    rol = serializers.ChoiceField(choices=[Usuario.Rol.PROFESOR, Usuario.Rol.ESTUDIANTE])

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'rol']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)
