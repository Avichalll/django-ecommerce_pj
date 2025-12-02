from django.contrib import admin

# Register your models here.
from rest_framework import serializers
from apps.cart.models import CartItem
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for reading cart items"""
    
    product = ProductListSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'quantity',
            'unit_price',
            'subtotal',
            'discount_amount',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding items to cart"""
    
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source='product',
        write_only=True,
        error_messages={
            'does_not_exist': 'Product with this ID does not exist.',
            'null': 'Product ID is required.'
        }
    )
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']
    
    def validate_product_id(self, value):
        """Validate product is available"""
        if not value.is_active:
            raise serializers.ValidationError("This product is not available.")
        if value.quantity <= 0:
            raise serializers.ValidationError("This product is out of stock.")
        return value
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)
        
        if quantity > product.quantity:
            raise serializers.ValidationError({
                'quantity': f"Only {product.quantity} items available in stock."
            })
        
        return attrs
    
    def create(self, validated_data):
        """Add item to cart or update quantity if exists"""
        cart = self.context.get('cart')
        product = validated_data['product']
        quantity = validated_data['quantity']
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity
            cart_item.quantity += quantity
            if cart_item.quantity > product.quantity:
                raise serializers.ValidationError({
                    'quantity': f"Cannot add more. Only {product.quantity} items available."
                })
            cart_item.save()
        
        return cart_item


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity"""
    
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        
        product = self.instance.product
        if value > product.quantity:
            raise serializers.ValidationError(
                f"Only {product.quantity} items available in stock."
            )
        
        return value