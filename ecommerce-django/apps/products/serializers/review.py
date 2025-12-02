from rest_framework import serializers
from apps.products.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id',
            'product',
            'user',
            'user_name',
            'rating',
            'title',
            'comment',
            'is_verified_purchase',
            'is_approved',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'is_approved', 'created_at', 'updated_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['product', 'rating', 'title', 'comment']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)