"""Renderiza las páginas de profesor y administración."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from apps.courses.models import Curso
from apps.enrollments.models import Inscripcion
from apps.enrollments.services import inscribir_estudiante
from apps.orders.models import Orden
from apps.users.models import Usuario
from .web_forms import CursoForm, InscripcionAdminForm, ProfesorForm
from .web_views import _error_de_servicio


class RoleLoginView(LoginView):
    template_name = 'web/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        destino = self.get_redirect_url()
        if destino:
            return destino
        if self.request.user.is_superuser:
            return reverse('web_admin_dashboard')
        if self.request.user.rol == Usuario.Rol.PROFESOR:
            return reverse('web_profesor_cursos')
        return reverse('web_catalogo')


def _admin(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Esta página requiere una cuenta administradora.')


def _profesor(request):
    if request.user.rol != Usuario.Rol.PROFESOR or request.user.is_superuser:
        raise PermissionDenied('Esta página es para profesores.')


@login_required
def profesor_cursos(request):
    _profesor(request)
    cursos = Curso.objects.filter(profesores=request.user).annotate(
        inscritos=Count('inscripciones', filter=Q(inscripciones__estado=Inscripcion.Estado.CONFIRMADA))
    ).order_by('fecha_inicio')
    return render(request, 'web/profesor_cursos.html', {'cursos': cursos})


@login_required
def profesor_curso(request, pk):
    _profesor(request)
    curso = get_object_or_404(Curso, pk=pk, profesores=request.user)
    estudiantes = Inscripcion.objects.filter(
        curso=curso, estado=Inscripcion.Estado.CONFIRMADA
    ).select_related('estudiante').order_by('estudiante__last_name', 'estudiante__username')
    return render(request, 'web/profesor_curso.html', {
        'curso': curso,
        'estudiantes': estudiantes,
    })


@login_required
def admin_dashboard(request):
    _admin(request)
    return render(request, 'web/admin_dashboard.html', {
        'total_cursos': Curso.objects.count(),
        'cursos_publicados': Curso.objects.filter(estado=Curso.Estado.PUBLICADO).count(),
        'total_profesores': Usuario.objects.filter(rol=Usuario.Rol.PROFESOR).count(),
        'inscripciones_confirmadas': Inscripcion.objects.filter(estado=Inscripcion.Estado.CONFIRMADA).count(),
        'ordenes_pendientes': Orden.objects.filter(estado=Orden.Estado.PENDIENTE).count(),
    })


@login_required
def admin_cursos(request):
    _admin(request)
    cursos = Curso.objects.prefetch_related('profesores').order_by('-id')
    return render(request, 'web/admin_cursos.html', {'cursos': cursos})


@login_required
def admin_curso_form(request, pk=None):
    _admin(request)
    curso = get_object_or_404(Curso, pk=pk) if pk is not None else None
    form = CursoForm(request.POST or None, instance=curso)
    if request.method == 'POST' and form.is_valid():
        curso = form.save()
        messages.success(request, 'Curso guardado.')
        return redirect('web_admin_cursos')
    return render(request, 'web/admin_curso_form.html', {
        'form': form,
        'curso': curso,
    })


@login_required
def admin_profesores(request):
    _admin(request)
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR).prefetch_related(
        'cursos_dictados'
    ).order_by('username')
    return render(request, 'web/admin_profesores.html', {'profesores': profesores})


@login_required
def admin_profesor_nuevo(request):
    _admin(request)
    form = ProfesorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profesor creado. Ya puedes asignarle cursos.')
        return redirect('web_admin_profesores')
    return render(request, 'web/admin_profesor_form.html', {'form': form})


@login_required
def admin_inscripciones(request):
    _admin(request)
    inscripciones = Inscripcion.objects.select_related('estudiante', 'curso').order_by('-creada_en')
    return render(request, 'web/admin_inscripciones.html', {
        'inscripciones': inscripciones,
    })


@login_required
def admin_inscripcion_nueva(request):
    _admin(request)
    form = InscripcionAdminForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            inscribir_estudiante(form.cleaned_data['estudiante'], form.cleaned_data['curso'].pk)
            messages.success(request, 'Estudiante inscrito directamente.')
            return redirect('web_admin_inscripciones')
        except ValidationError as exc:
            form.add_error(None, _error_de_servicio(exc))
    return render(request, 'web/admin_inscripcion_form.html', {'form': form})


@login_required
def admin_ordenes(request):
    _admin(request)
    ordenes = Orden.objects.select_related('usuario').prefetch_related(
        'items__curso'
    ).order_by('-creada_en')
    return render(request, 'web/admin_ordenes.html', {'ordenes': ordenes})

