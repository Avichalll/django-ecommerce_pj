from rest_framework import serializers
from apps.products.models import Category


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 
            'name', 
            'slug', 
            'description', 
            'image', 
            'parent', 
            'children',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'name' 'created_at', 'updated_at']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data


class CategoryListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']