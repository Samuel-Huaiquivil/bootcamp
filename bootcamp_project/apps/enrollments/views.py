from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.courses.models import Curso
from apps.orders.services import bloquear_curso, cancelar_inscripcion, cupos_disponibles, validar_compra
from apps.users.models import Usuario
from apps.users.permissions import EsAdministrador, EsEstudiante
from .models import Inscripcion
from .serializers import InscripcionSerializer


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

    @transaction.atomic
    def post(self, request):
        estudiante = get_object_or_404(Usuario, pk=request.data.get('estudiante_id'), rol=Usuario.Rol.ESTUDIANTE)
        curso = get_object_or_404(Curso, pk=request.data.get('curso_id'))
        curso = bloquear_curso(curso.pk)
        validar_compra(estudiante, curso)
        if cupos_disponibles(curso) < 1:
            raise ValidationError('No quedan cupos disponibles.')
        inscripcion, _ = Inscripcion.objects.update_or_create(estudiante=estudiante, curso=curso,
                                                               defaults={'estado': Inscripcion.Estado.CONFIRMADA})
        return Response(InscripcionSerializer(inscripcion).data, status=status.HTTP_201_CREATED)
