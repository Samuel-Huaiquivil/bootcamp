from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.cart.models import ItemCarrito
from apps.enrollments.models import Inscripcion
from apps.orders.models import Orden
from apps.users.models import Usuario
from .models import Curso


class FlujoCompraTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser('admin', 'admin@example.com', 'clave-segura-123')
        self.estudiante = Usuario.objects.create_user('ana', 'ana@example.com', 'clave-segura-123')
        self.profesor = Usuario.objects.create_user('profe', 'profe@example.com', 'clave-segura-123', rol=Usuario.Rol.PROFESOR)
        self.curso = Curso.objects.create(
            nombre='Django inicial', cupos=1, precio=Decimal('100.00'), estado=Curso.Estado.PUBLICADO,
            fecha_inicio=timezone.now() + timedelta(days=3),
            fecha_termino=timezone.now() + timedelta(days=10),
            fecha_limite_inscripcion=timezone.now() + timedelta(days=2),
        )
        self.cliente = APIClient()
        self.cliente.force_authenticate(self.estudiante)

    def test_compra_cancelacion_y_recompra(self):
        respuesta = self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk})
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 400)
        orden = self.cliente.post('/api/ordenes/crear/').data
        self.assertEqual(Decimal(orden['total']), Decimal('100.00'))
        pago = self.cliente.post(f"/api/ordenes/{orden['id']}/pagar/", {'aprobar': True}, format='json')
        self.assertEqual(pago.status_code, 200)
        self.assertEqual(pago.data['estado'], Orden.Estado.PAGADA)
        inscripcion = Inscripcion.objects.get(estudiante=self.estudiante, curso=self.curso)
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 400)
        cancelacion = self.cliente.post(f'/api/inscripciones/{inscripcion.pk}/cancelar/')
        self.assertEqual(cancelacion.status_code, 200)
        self.assertEqual(Orden.objects.get(pk=orden['id']).estado, Orden.Estado.REEMBOLSADA)
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 201)

    def test_reserva_expirada_libera_cupo(self):
        self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk})
        otro = Usuario.objects.create_user('otro', 'otro@example.com', 'clave-segura-123')
        self.cliente.force_authenticate(otro)
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 400)
        ItemCarrito.objects.update(reservado_hasta=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 201)

    def test_roles_y_fecha_inicio(self):
        self.cliente.force_authenticate(self.profesor)
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 403)
        self.cliente.force_authenticate(self.estudiante)
        self.assertEqual(self.cliente.get('/api/gestion/cursos/').status_code, 403)
        self.curso.fecha_inicio = timezone.now() - timedelta(minutes=1)
        self.curso.save()
        self.assertEqual(self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk}).status_code, 400)

    def test_jwt(self):
        self.cliente.force_authenticate(user=None)
        respuesta = self.cliente.post('/api/token/', {'username': 'ana', 'password': 'clave-segura-123'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('access', respuesta.data)

    def test_orden_expirada_se_cancela(self):
        self.cliente.post('/api/carrito/agregar/', {'curso_id': self.curso.pk})
        orden = self.cliente.post('/api/ordenes/crear/').data
        Orden.objects.filter(pk=orden['id']).update(estado=Orden.Estado.PENDIENTE)
        from apps.orders.models import ItemOrden
        ItemOrden.objects.filter(orden_id=orden['id']).update(reservado_hasta=timezone.now() - timedelta(seconds=1))
        respuesta = self.cliente.post(f"/api/ordenes/{orden['id']}/pagar/", {'aprobar': True}, format='json')
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(Orden.objects.get(pk=orden['id']).estado, Orden.Estado.CANCELADA)

    def test_administracion_de_profesores(self):
        self.cliente.force_authenticate(self.admin)
        respuesta = self.cliente.post(f'/api/gestion/cursos/{self.curso.pk}/profesores/',
                                     {'profesor_id': self.profesor.pk})
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(self.profesor.pk, respuesta.data['profesores'])
        self.cliente.force_authenticate(self.estudiante)
        self.assertEqual(self.cliente.post(f'/api/gestion/cursos/{self.curso.pk}/profesores/',
                                          {'profesor_id': self.profesor.pk}).status_code, 403)
