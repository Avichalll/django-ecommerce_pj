
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.products.models import Review

class ReviewViewSet(viewsets.ModelViewSet):
    queryset= Review.objects.filter(is_approved=True)
    
