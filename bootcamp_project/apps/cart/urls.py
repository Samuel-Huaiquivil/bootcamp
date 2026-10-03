from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CartViewSet

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course')
router.register('cart', CartViewSet, basename='cart')

urlpatterns = router.urls