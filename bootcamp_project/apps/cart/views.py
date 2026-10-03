from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Course, Cart, CartItem
from .serializers import CourseSerializer, CartSerializer, CartItemSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        cart = self._get_cart(request)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self._get_cart(request)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data['course']
        quantity = serializer.validated_data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart, course=course,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        cart = self._get_cart(request)
        item_id = request.data.get('item_id')
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self._get_cart(request)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)