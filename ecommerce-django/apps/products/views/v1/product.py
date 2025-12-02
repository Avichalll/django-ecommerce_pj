from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction

from apps.products.models import Category, Product
from apps.products.serializers import (
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductCreateSerializer,
    ProductListSerializer
)


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.filter(is_active=True)
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        # Return full product details
        response_serializer = ProductDetailSerializer(product)
        
        return Response(
            {
                "success": True,
                "message": "Product created successfully.",
                "data": response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)