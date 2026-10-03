from django.contrib import admin
from .models import Course, Cart, CartItem

admin.site.register(Course)
admin.site.register(Cart)
admin.site.register(CartItem)