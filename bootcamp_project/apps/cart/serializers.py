"""Serializa el carrito y los cursos reservados para la API."""

from rest_framework import serializers
from .models import Carrito, ItemCarrito


class ItemCarritoSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)

    class Meta:
        model = ItemCarrito
        fields = ['id', 'curso', 'curso_nombre', 'precio', 'reservado_hasta']


class CarritoSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = Carrito
        fields = ['id', 'items', 'subtotal', 'creado_en']

    def get_items(self, obj):
        from django.utils import timezone
        return ItemCarritoSerializer(obj.items.filter(reservado_hasta__gt=timezone.now()), many=True).data
