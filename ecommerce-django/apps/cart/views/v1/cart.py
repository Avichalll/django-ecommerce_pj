from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction

from apps.cart.models import Cart, CartItem
from apps.cart.serializers import (
    CartSerializer,
    CartSummarySerializer,
    CartItemSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer
)


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for cart operations.
    
    Endpoints:
    - GET    /cart/              - Get current cart
    - POST   /cart/add/          - Add item to cart
    - PATCH  /cart/update/{id}/  - Update item quantity
    - DELETE /cart/remove/{id}/  - Remove item from cart
    - DELETE /cart/clear/        - Clear entire cart
    - GET    /cart/summary/      - Get cart summary
    """
    
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        """Get or create cart for current user/session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        return cart
    
    def list(self, request):
        """Get current cart with all items"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get cart summary (item count and total)"""
        cart = self.get_cart(request)
        serializer = CartSummarySerializer(cart)
        
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def add(self, request):
        """Add item to cart"""
        cart = self.get_cart(request)
        
        serializer = CartItemCreateSerializer(
            data=request.data,
            context={'cart': cart, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        cart_item = serializer.save()
        
        return Response({
            "success": True,
            "message": "Item added to cart.",
            "data": CartItemSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch'], url_path='update/(?P<item_id>[^/.]+)')
    @transaction.atomic
    def update_item(self, request, item_id=None):
        """Update cart item quantity"""
        cart = self.get_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Item not found in cart."
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartItemUpdateSerializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "success": True,
            "message": "Cart item updated.",
            "data": CartItemSerializer(cart_item).data
        })
    
    @action(detail=False, methods=['delete'], url_path='remove/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart"""
        cart = self.get_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Item not found in cart."
            }, status=status.HTTP_404_NOT_FOUND)
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        return Response({
            "success": True,
            "message": f"'{product_name}' removed from cart."
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_cart(request)
        item_count = cart.items.count()
        cart.clear()
        
        return Response({
            "success": True,
            "message": f"Cart cleared. {item_count} item(s) removed."
        })
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def merge(self, request):
        """
        Merge anonymous cart with user cart after login.
        Call this after user authentication.
        """
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "User must be authenticated."
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        session_key = request.session.session_key
        if not session_key:
            return Response({
                "success": True,
                "message": "No anonymous cart to merge."
            })
        
        try:
            anonymous_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
        except Cart.DoesNotExist:
            return Response({
                "success": True,
                "message": "No anonymous cart to merge."
            })
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Merge items
        for item in anonymous_cart.items.all():
            existing_item = user_cart.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                if existing_item.quantity > item.product.quantity:
                    existing_item.quantity = item.product.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        
        # Delete anonymous cart
        anonymous_cart.delete()
        
        return Response({
            "success": True,
            "message": "Carts merged successfully.",
            "data": CartSerializer(user_cart).data
        })