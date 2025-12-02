from rest_framework import serializers
from apps.products.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product',
            'image',
            'alt_text',
            'is_primary',
            'order',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    
class ProductImageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=ProductImage
        fields= [
            'image',
            'alt_text',
            'is_primary',
            'order'
        ]
