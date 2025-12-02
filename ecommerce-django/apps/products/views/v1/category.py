
from rest_framework import viewsets
from apps.products.models import Category
from apps.products.serializers import CategoryListSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    
    queryset= Category.objects.filter(is_active=True)
    serializer_class= CategoryListSerializer