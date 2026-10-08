"""Gestiona consultas, cancelaciones e inscripciones desde la API."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.courses.models import Curso
from apps.orders.services import cancelar_inscripcion
from apps.users.models import Usuario
from apps.users.permissions import EsAdministrador, EsEstudiante
from .models import Inscripcion
from .serializers import InscripcionSerializer
from .services import inscribir_estudiante


class InscripcionesView(generics.ListAPIView):
    permission_classes = [EsEstudiante]
    serializer_class = InscripcionSerializer

    def get_queryset(self):
        return Inscripcion.objects.filter(estudiante=self.request.user).order_by('-creada_en')


class CancelarInscripcionView(APIView):
    permission_classes = [EsEstudiante]

    def post(self, request, pk):
        get_object_or_404(Inscripcion, pk=pk, estudiante=request.user)
        return Response(InscripcionSerializer(cancelar_inscripcion(request.user, pk)).data)


class InscribirAdminView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request):
        estudiante = get_object_or_404(Usuario, pk=request.data.get('estudiante_id'), rol=Usuario.Rol.ESTUDIANTE)
        curso = get_object_or_404(Curso, pk=request.data.get('curso_id'))
        inscripcion = inscribir_estudiante(estudiante, curso.pk)
        return Response(InscripcionSerializer(inscripcion).data, status=status.HTTP_201_CREATED)
