from rest_framework import serializers
from apps.cart.models import Cart
from .cart_item import CartItemSerializer


class CartSerializer(serializers.ModelSerializer):
    """Serializer for reading cart"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_items',
            'subtotal',
            'total_discount',
            'total',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartSummarySerializer(serializers.ModelSerializer):
    """Lightweight cart summary serializer"""
    
    total_items = serializers.IntegerField(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'total_items', 'total']