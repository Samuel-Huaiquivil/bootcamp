"""Expone el historial de órdenes y las acciones de compra por API."""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.permissions import EsAdministrador, EsEstudiante
from .models import Orden
from .serializers import OrdenSerializer
from .services import crear_orden, pagar_orden


class OrdenesView(generics.ListAPIView):
    permission_classes = [EsEstudiante]
    serializer_class = OrdenSerializer

    def get_queryset(self):
        return Orden.objects.filter(usuario=self.request.user).order_by('-creada_en')


class CrearOrdenView(APIView):
    permission_classes = [EsEstudiante]

    def post(self, request):
        orden = crear_orden(request.user)
        return Response(OrdenSerializer(orden).data, status=status.HTTP_201_CREATED)


class PagarOrdenView(APIView):
    permission_classes = [EsEstudiante]

    def post(self, request, pk):
        if type(request.data.get('aprobar')) is not bool:
            return Response({'aprobar': 'Envía true o false.'}, status=status.HTTP_400_BAD_REQUEST)
        from django.shortcuts import get_object_or_404
        get_object_or_404(Orden, pk=pk, usuario=request.user)
        orden = pagar_orden(request.user, pk, request.data['aprobar'])
        codigo = status.HTTP_409_CONFLICT if orden.estado == Orden.Estado.CANCELADA else status.HTTP_200_OK
        return Response(OrdenSerializer(orden).data, status=codigo)


class OrdenesAdminView(generics.ListAPIView):
    permission_classes = [EsAdministrador]
    serializer_class = OrdenSerializer
    queryset = Orden.objects.all().order_by('-creada_en')
