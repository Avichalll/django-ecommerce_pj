from django.db import models
from django.contrib.auth import get_user_model
from .category import Category

User = get_user_model()


class Product(models.Model):

    class STOCK_STATUS(models.TextChoices):
        IN_STOCK= 'In_Stock'
        OUT_OF_STOCK= 'Out_Of_Stock',
        LOW_STOCK= 'Low_Stock'


    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sku = models.CharField(max_length=50, unique=True)  
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    quantity = models.PositiveIntegerField(default=0)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS, default=STOCK_STATUS.IN_STOCK)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    brand = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True)  
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name



    @property
    def current_price(self):
        return self.discount_price if self.is_on_sale else self.price