from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator , MaxValueValidator

from .product import Product

User = get_user_model()

class Review(models.Model):

    product= models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating= models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    title= models.CharField(max_length=100)
    comment= models.TextField()
    is_verfied_purchase= models.BooleanField(default=True)
    is_approved= models.BooleanField(default=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering= ['-created_at']
        unique_together=['product', 'user']





