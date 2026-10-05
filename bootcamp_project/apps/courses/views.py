from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models import Usuario
from apps.users.permissions import EsAdministrador
from .models import Curso
from .serializers import CursoSerializer


class CursoListaView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CursoSerializer
    queryset = Curso.objects.filter(estado=Curso.Estado.PUBLICADO).order_by('fecha_inicio')


class CursoDetalleView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CursoSerializer
    queryset = Curso.objects.filter(estado=Curso.Estado.PUBLICADO)


class CursosAdminView(generics.ListCreateAPIView):
    permission_classes = [EsAdministrador]
    serializer_class = CursoSerializer
    queryset = Curso.objects.all().order_by('-id')


class CursoAdminDetalleView(generics.RetrieveUpdateAPIView):
    permission_classes = [EsAdministrador]
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()


class AsignarProfesorView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request, pk):
        curso = get_object_or_404(Curso, pk=pk)
        profesor = get_object_or_404(Usuario, pk=request.data.get('profesor_id'), rol=Usuario.Rol.PROFESOR)
        curso.profesores.add(profesor)
        return Response(CursoSerializer(curso).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        curso = get_object_or_404(Curso, pk=pk)
        profesor = get_object_or_404(Usuario, pk=request.data.get('profesor_id'), rol=Usuario.Rol.PROFESOR)
        curso.profesores.remove(profesor)
        return Response(status=status.HTTP_204_NO_CONTENT)
