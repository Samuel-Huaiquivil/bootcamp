from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Usuario
from .permissions import EsAdministrador
from .serializers import RegistroSerializer, UsuarioSerializer, CrearUsuarioAdminSerializer


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]


class MiPerfilView(generics.RetrieveAPIView):
    serializer_class = UsuarioSerializer

    def get_object(self):
        return self.request.user


class UsuariosAdminView(generics.ListCreateAPIView):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = [EsAdministrador]

    def get_serializer_class(self):
        return CrearUsuarioAdminSerializer if self.request.method == 'POST' else UsuarioSerializer
