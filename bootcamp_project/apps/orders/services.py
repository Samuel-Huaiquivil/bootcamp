"""Coordina reservas, compras, pagos simulados y reembolsos."""

from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.cart.models import Carrito, ItemCarrito
from apps.courses.models import Curso
from apps.enrollments.models import Inscripcion
from .models import ItemOrden, Orden, Pago


def cupos_disponibles(curso):
    ahora = timezone.now()
    confirmadas = Inscripcion.objects.filter(curso=curso, estado=Inscripcion.Estado.CONFIRMADA).count()
    en_carrito = ItemCarrito.objects.filter(curso=curso, reservado_hasta__gt=ahora).count()
    en_orden = ItemOrden.objects.filter(
        curso=curso, estado=ItemOrden.Estado.PENDIENTE,
        orden__estado=Orden.Estado.PENDIENTE, reservado_hasta__gt=ahora,
    ).count()
    return max(0, curso.cupos - confirmadas - en_carrito - en_orden)


def bloquear_curso(curso_id):
    # El incremento toma un bloqueo de escritura incluso en SQLite.
    Curso.objects.filter(pk=curso_id).update(version_cupos=F('version_cupos') + 1)
    return Curso.objects.select_for_update().get(pk=curso_id)


def validar_compra(usuario, curso):
    if not curso.disponible_para_compra():
        raise ValidationError('El curso no está disponible para compra.')
    if Inscripcion.objects.filter(estudiante=usuario, curso=curso).exclude(estado=Inscripcion.Estado.CANCELADA).exists():
        raise ValidationError('Ya tienes una inscripción en este curso.')
    if ItemOrden.objects.filter(orden__usuario=usuario, curso=curso, orden__estado=Orden.Estado.PENDIENTE,
                                reservado_hasta__gt=timezone.now()).exists():
        raise ValidationError('Ya tienes una orden pendiente para este curso.')


@transaction.atomic
def agregar_al_carrito(usuario, curso_id):
    curso = bloquear_curso(curso_id)
    validar_compra(usuario, curso)
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    item = ItemCarrito.objects.filter(carrito=carrito, curso=curso).first()
    if item and item.reservado_hasta > timezone.now():
        raise ValidationError('El curso ya está en tu carrito.')
    if cupos_disponibles(curso) < 1:
        raise ValidationError('No quedan cupos disponibles.')
    if item:
        item.precio = curso.precio
        item.reservado_hasta = timezone.now() + timedelta(minutes=15)
        item.save(update_fields=['precio', 'reservado_hasta'])
    else:
        item = ItemCarrito.objects.create(carrito=carrito, curso=curso, precio=curso.precio,
                                         reservado_hasta=timezone.now() + timedelta(minutes=15))
    return item


@transaction.atomic
def crear_orden(usuario):
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    items = list(carrito.items.filter(reservado_hasta__gt=timezone.now()).order_by('curso_id'))
    if not items:
        raise ValidationError('El carrito no tiene reservas vigentes.')
    for item in items:
        curso = bloquear_curso(item.curso_id)
        validar_compra(usuario, curso)
        if item.reservado_hasta <= timezone.now():
            raise ValidationError('Una reserva expiró. Vuelve a agregar el curso.')
    total = sum((item.precio for item in items), Decimal('0'))
    orden = Orden.objects.create(usuario=usuario, total=total)
    for item in items:
        ItemOrden.objects.create(orden=orden, curso=item.curso, precio=item.precio,
                                reservado_hasta=item.reservado_hasta)
    carrito.items.filter(pk__in=[item.pk for item in items]).delete()
    Pago.objects.create(orden=orden)
    return orden


@transaction.atomic
def pagar_orden(usuario, orden_id, aprobar):
    orden = Orden.objects.select_for_update().get(pk=orden_id, usuario=usuario)
    if orden.estado != Orden.Estado.PENDIENTE:
        raise ValidationError('La orden ya fue procesada.')
    items = list(orden.items.order_by('curso_id'))
    for item in items:
        curso = bloquear_curso(item.curso_id)
        if item.reservado_hasta <= timezone.now() or not curso.disponible_para_compra():
            orden.estado = Orden.Estado.CANCELADA
            orden.save(update_fields=['estado'])
            return orden
    pago = orden.pago
    if not aprobar:
        pago.estado = Pago.Estado.RECHAZADO
        orden.estado = Orden.Estado.FALLIDA
    else:
        for item in items:
            inscripcion, creada = Inscripcion.objects.get_or_create(
                estudiante=usuario, curso=item.curso,
                defaults={'estado': Inscripcion.Estado.CONFIRMADA},
            )
            if not creada and inscripcion.estado != Inscripcion.Estado.CANCELADA:
                raise ValidationError('Ya estás inscrito en uno de los cursos.')
            if not creada:
                inscripcion.estado = Inscripcion.Estado.CONFIRMADA
                inscripcion.save(update_fields=['estado'])
            item.estado = ItemOrden.Estado.PAGADO
            item.save(update_fields=['estado'])
        pago.estado = Pago.Estado.APROBADO
        orden.estado = Orden.Estado.PAGADA
    pago.save(update_fields=['estado', 'actualizado_en'])
    orden.save(update_fields=['estado'])
    return orden


@transaction.atomic
def cancelar_inscripcion(usuario, inscripcion_id):
    inscripcion = Inscripcion.objects.select_for_update().get(pk=inscripcion_id, estudiante=usuario)
    curso = bloquear_curso(inscripcion.curso_id)
    if inscripcion.estado != Inscripcion.Estado.CONFIRMADA:
        raise ValidationError('La inscripción no está confirmada.')
    if timezone.now() >= curso.fecha_inicio:
        raise ValidationError('Solo se puede cancelar antes del inicio del curso.')
    item = ItemOrden.objects.filter(orden__usuario=usuario, curso=curso, estado=ItemOrden.Estado.PAGADO).first()
    inscripcion.estado = Inscripcion.Estado.CANCELADA
    inscripcion.save(update_fields=['estado'])
    if item:
        item.estado = ItemOrden.Estado.REEMBOLSADO
        item.save(update_fields=['estado'])
        pago = item.orden.pago
        pago.monto_reembolsado += item.precio
        if pago.monto_reembolsado >= item.orden.total:
            pago.estado = Pago.Estado.REEMBOLSADO
            item.orden.estado = Orden.Estado.REEMBOLSADA
            item.orden.save(update_fields=['estado'])
        pago.save(update_fields=['monto_reembolsado', 'estado', 'actualizado_en'])
    return inscripcion
