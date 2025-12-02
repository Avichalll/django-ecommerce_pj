from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.cart.views.v1 import CartViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]