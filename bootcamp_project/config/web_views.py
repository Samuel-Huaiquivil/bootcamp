from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.cart.models import Carrito, ItemCarrito
from apps.courses.models import Curso
from apps.enrollments.models import Inscripcion
from apps.orders.models import Orden
from apps.orders.services import (
    agregar_al_carrito,
    bloquear_curso,
    cancelar_inscripcion,
    crear_orden,
    cupos_disponibles,
    pagar_orden,
)
from apps.users.models import Usuario
from .web_forms import RegistroForm


def _estudiante(request):
    if request.user.is_superuser or request.user.rol != Usuario.Rol.ESTUDIANTE:
        raise PermissionDenied('Esta página es para estudiantes.')


def _solo_post(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    return None


def _error_de_servicio(exc):
    detalle = exc.detail
    if isinstance(detalle, list):
        return ' '.join(str(item) for item in detalle)
    return str(detalle)


def catalogo(request):
    cursos = Curso.objects.filter(estado=Curso.Estado.PUBLICADO).order_by('fecha_inicio')
    return render(request, 'web/catalogo.html', {'cursos': cursos})


def detalle_curso(request, pk):
    curso = get_object_or_404(
        Curso.objects.prefetch_related('profesores'), pk=pk, estado=Curso.Estado.PUBLICADO
    )
    return render(request, 'web/curso.html', {
        'curso': curso,
        'cupos_disponibles': cupos_disponibles(curso),
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('web_catalogo')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, 'Tu cuenta está lista.')
        return redirect('web_catalogo')
    return render(request, 'web/registro.html', {'form': form})


@login_required
def carrito(request):
    _estudiante(request)
    carrito_actual, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito_actual.items.select_related('curso').filter(
        reservado_hasta__gt=timezone.now()
    ).order_by('curso__nombre')
    return render(request, 'web/carrito.html', {
        'items': items,
        'subtotal': carrito_actual.subtotal,
    })


@login_required
def agregar_curso(request, pk):
    if respuesta := _solo_post(request):
        return respuesta
    _estudiante(request)
    get_object_or_404(Curso, pk=pk, estado=Curso.Estado.PUBLICADO)
    try:
        agregar_al_carrito(request.user, pk)
        messages.success(request, 'Curso agregado al carrito. La reserva dura 15 minutos.')
        return redirect('web_carrito')
    except ValidationError as exc:
        messages.error(request, _error_de_servicio(exc))
        return redirect('web_curso', pk=pk)


@login_required
def quitar_curso(request, pk):
    if respuesta := _solo_post(request):
        return respuesta
    _estudiante(request)
    with transaction.atomic():
        item = get_object_or_404(ItemCarrito, pk=pk, carrito__usuario=request.user)
        bloquear_curso(item.curso_id)
        item.delete()
    messages.success(request, 'Curso quitado del carrito.')
    return redirect('web_carrito')


@login_required
def ordenes(request):
    _estudiante(request)
    historial = Orden.objects.filter(usuario=request.user).prefetch_related(
        'items__curso'
    ).order_by('-creada_en')
    return render(request, 'web/ordenes.html', {'ordenes': historial})


@login_required
def crear_orden_web(request):
    if respuesta := _solo_post(request):
        return respuesta
    _estudiante(request)
    try:
        orden = crear_orden(request.user)
        messages.success(request, 'Orden creada. Confirma el pago simulado antes de que venza la reserva.')
        return redirect('web_ordenes')
    except ValidationError as exc:
        messages.error(request, _error_de_servicio(exc))
        return redirect('web_carrito')


@login_required
def pagar_orden_web(request, pk):
    if respuesta := _solo_post(request):
        return respuesta
    _estudiante(request)
    get_object_or_404(Orden, pk=pk, usuario=request.user)
    try:
        orden = pagar_orden(request.user, pk, aprobar=True)
        if orden.estado == Orden.Estado.PAGADA:
            messages.success(request, 'Pago simulado aprobado. Tu inscripción está confirmada.')
        else:
            messages.error(request, 'La reserva venció o el curso ya no está disponible.')
    except ValidationError as exc:
        messages.error(request, _error_de_servicio(exc))
    return redirect('web_ordenes')


@login_required
def inscripciones(request):
    _estudiante(request)
    listado = Inscripcion.objects.filter(estudiante=request.user).select_related(
        'curso'
    ).order_by('-creada_en')
    return render(request, 'web/inscripciones.html', {
        'inscripciones': listado,
        'now': timezone.now(),
    })


@login_required
def cancelar_inscripcion_web(request, pk):
    if respuesta := _solo_post(request):
        return respuesta
    _estudiante(request)
    get_object_or_404(Inscripcion, pk=pk, estudiante=request.user)
    try:
        cancelar_inscripcion(request.user, pk)
        messages.success(request, 'Inscripción cancelada. Se registró el reembolso simulado.')
    except ValidationError as exc:
        messages.error(request, _error_de_servicio(exc))
    return redirect('web_inscripciones')
