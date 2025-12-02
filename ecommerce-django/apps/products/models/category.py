
from django.db import models


class Category(models.Model):
    
    name= models.CharField(max_length=100)
    slug= models.SlugField(max_length=100, unique=True)
    description= models.TextField(blank=True)
    image= models.ImageField(upload_to='categories/', blank=True, null=True)

    parent= models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children'
    )

    is_active= models.BooleanField(default=True)
    createdAt= models.DateTimeField(auto_now_add=True)
    updatedAt= models.DateTimeField(auto_now_add=True)
     
    class Meta:
        ordering=['name']

    def __str__(self):
        return self.name