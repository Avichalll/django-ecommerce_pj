
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views.v1 import ProductViewSet
from apps.products.views.v1 import CategoryViewSet


router= DefaultRouter()

router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
# router.register(r'images', ProductImageViewSet, basename='product-image')
# router.register(r'reviews', ReviewViewSet, basename='review')


urlpatterns = [
    path('', include(router.urls))
    
]
