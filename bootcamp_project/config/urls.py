"""
URL configuration for bootcamp_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

from . import web_views
from . import role_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.views import RegistroView, MiPerfilView, UsuariosAdminView
from apps.courses.views import (
    CursoListaView, 
    CursoDetalleView, 
    CursosAdminView, 
    CursoAdminDetalleView, 
    AsignarProfesorView
)
from apps.cart.views import CarritoView, AgregarCarritoView, QuitarCarritoView
from apps.orders.views import CrearOrdenView, OrdenesView, PagarOrdenView, OrdenesAdminView
from apps.enrollments.views import InscripcionesView, CancelarInscripcionView, InscribirAdminView

urlpatterns = [
    path('', web_views.catalogo, name='web_catalogo'),
    path('cursos/<int:pk>/', web_views.detalle_curso, name='web_curso'),
    path('registro/', web_views.registro, name='web_registro'),
    path('ingresar/', role_views.RoleLoginView.as_view(), name='web_login'),
    path('docencia/', role_views.profesor_cursos, name='web_profesor_cursos'),
    path('docencia/cursos/<int:pk>/', role_views.profesor_curso, name='web_profesor_curso'),
    path('gestion/', role_views.admin_dashboard, name='web_admin_dashboard'),
    path('gestion/cursos/', role_views.admin_cursos, name='web_admin_cursos'),
    path('gestion/cursos/nuevo/', role_views.admin_curso_form, name='web_admin_curso_nuevo'),
    path('gestion/cursos/<int:pk>/editar/', role_views.admin_curso_form, name='web_admin_curso_editar'),
    path('gestion/profesores/', role_views.admin_profesores, name='web_admin_profesores'),
    path('gestion/profesores/nuevo/', role_views.admin_profesor_nuevo, name='web_admin_profesor_nuevo'),
    path('gestion/inscripciones/', role_views.admin_inscripciones, name='web_admin_inscripciones'),
    path('gestion/inscripciones/nueva/', role_views.admin_inscripcion_nueva, name='web_admin_inscripcion_nueva'),
    path('gestion/ordenes/', role_views.admin_ordenes, name='web_admin_ordenes'),

    # Vista Web
    path(
        'salir/',
        auth_views.LogoutView.as_view(next_page='web_catalogo'),
        name='web_logout',
    ),
    path('carrito/', web_views.carrito, name='web_carrito'),
    path('carrito/agregar/<int:pk>/', web_views.agregar_curso, name='web_agregar'),
    path('carrito/quitar/<int:pk>/', web_views.quitar_curso, name='web_quitar'),
    path('ordenes/', web_views.ordenes, name='web_ordenes'),
    path('ordenes/crear/', web_views.crear_orden_web, name='web_crear_orden'),
    path('ordenes/<int:pk>/pagar/', web_views.pagar_orden_web, name='web_pagar_orden'),
    path('inscripciones/', web_views.inscripciones, name='web_inscripciones'),
    path('inscripciones/<int:pk>/cancelar/', web_views.cancelar_inscripcion_web, name='web_cancelar_inscripcion'),


    path('api/registro/', RegistroView.as_view()),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/renovar/', TokenRefreshView.as_view()),
    path('api/yo/', MiPerfilView.as_view()),
    path('api/cursos/', CursoListaView.as_view()),
    path('api/cursos/<int:pk>/', CursoDetalleView.as_view()),
    path('api/carrito/', CarritoView.as_view()),
    path('api/carrito/agregar/', AgregarCarritoView.as_view()),
    path('api/carrito/quitar/<int:pk>/', QuitarCarritoView.as_view()),
    path('api/ordenes/', OrdenesView.as_view()),
    path('api/ordenes/crear/', CrearOrdenView.as_view()),
    path('api/ordenes/<int:pk>/pagar/', PagarOrdenView.as_view()),
    path('api/inscripciones/', InscripcionesView.as_view()),
    path('api/inscripciones/<int:pk>/cancelar/', CancelarInscripcionView.as_view()),
    path('api/gestion/usuarios/', UsuariosAdminView.as_view()),
    path('api/gestion/cursos/', CursosAdminView.as_view()),
    path('api/gestion/cursos/<int:pk>/', CursoAdminDetalleView.as_view()),
    path('api/gestion/cursos/<int:pk>/profesores/', AsignarProfesorView.as_view()),
    path('api/gestion/inscripciones/', InscribirAdminView.as_view()),
    path('api/gestion/ordenes/', OrdenesAdminView.as_view()),

    # Esquemas
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name="swagger-ui"),
    
    # Redirección de rutas inválidas
    re_path(r'^.*$', lambda request: redirect('/', permanent=False)),
]
