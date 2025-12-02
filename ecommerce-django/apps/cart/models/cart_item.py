from django.db import models
from django.core.validators import MinValueValidator
from apps.products.models import Product


class CartItem(models.Model):
    """
    Individual item in a shopping cart.
    """
    
    cart = models.ForeignKey(
        'cart.Cart',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def unit_price(self):
        """Get the current price of the product"""
        return self.product.current_price
    
    @property
    def original_price(self):
        """Get the original price without discount"""
        return self.product.price
    
    @property
    def subtotal(self):
        """Get subtotal for this item (quantity * unit_price)"""
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        """Get discount amount for this item"""
        if self.product.discount_price:
            return self.quantity * (self.product.price - self.product.discount_price)
        return 0
    
    def save(self, *args, **kwargs):
        # Validate stock availability
        if self.quantity > self.product.quantity:
            raise ValueError(f"Only {self.product.quantity} items available in stock.")
        super().save(*args, **kwargs)