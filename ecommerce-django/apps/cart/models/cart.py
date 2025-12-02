from django.db import models
from django.conf import settings
import uuid


class Cart(models.Model):
    """
    Shopping cart model.
    Can be associated with a user or be anonymous (session-based).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart {self.id}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Get cart subtotal before discounts"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total_discount(self):
        """Get total discount amount"""
        return sum(item.discount_amount for item in self.items.all())
    
    @property
    def total(self):
        """Get cart total after discounts"""
        return self.subtotal - self.total_discount
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()