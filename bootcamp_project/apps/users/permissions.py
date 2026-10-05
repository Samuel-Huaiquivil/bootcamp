from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_superuser)


class EsEstudiante(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.rol == request.user.Rol.ESTUDIANTE)
