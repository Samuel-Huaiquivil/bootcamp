from django.shortcuts import get_object_or_404
from django.db import transaction
"""Gestiona las consultas y modificaciones del carrito por API."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.courses.models import Curso
from apps.orders.services import agregar_al_carrito, bloquear_curso
from apps.users.permissions import EsEstudiante
from .models import Carrito, ItemCarrito
from .serializers import CarritoSerializer, ItemCarritoSerializer


class CarritoView(APIView):
    permission_classes = [EsEstudiante]

    def get(self, request):
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        return Response(CarritoSerializer(carrito).data)


class AgregarCarritoView(APIView):
    permission_classes = [EsEstudiante]

    def post(self, request):
        curso = get_object_or_404(Curso, pk=request.data.get('curso_id'))
        item = agregar_al_carrito(request.user, curso.pk)
        return Response(ItemCarritoSerializer(item).data, status=status.HTTP_201_CREATED)


class QuitarCarritoView(APIView):
    permission_classes = [EsEstudiante]

    @transaction.atomic
    def delete(self, request, pk):
        item = get_object_or_404(ItemCarrito, pk=pk, carrito__usuario=request.user)
        bloquear_curso(item.curso_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
