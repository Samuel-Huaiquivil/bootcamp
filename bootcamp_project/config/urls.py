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
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.views import RegistroView, MiPerfilView, UsuariosAdminView
from apps.courses.views import CursoListaView, CursoDetalleView, CursosAdminView, CursoAdminDetalleView, AsignarProfesorView
from apps.cart.views import CarritoView, AgregarCarritoView, QuitarCarritoView
from apps.orders.views import CrearOrdenView, OrdenesView, PagarOrdenView, OrdenesAdminView
from apps.enrollments.views import InscripcionesView, CancelarInscripcionView, InscribirAdminView

urlpatterns = [
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
]
