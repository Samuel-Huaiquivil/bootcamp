from rest_framework import serializers
from .models import Orden, ItemOrden, Pago


class ItemOrdenSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)

    class Meta:
        model = ItemOrden
        fields = ['id', 'curso', 'curso_nombre', 'precio', 'reservado_hasta', 'estado']


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['estado', 'monto_reembolsado']


class OrdenSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(many=True, read_only=True)
    pago = PagoSerializer(read_only=True)

    class Meta:
        model = Orden
        fields = ['id', 'numero', 'estado', 'total', 'creada_en', 'items', 'pago']
