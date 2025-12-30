from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .serializers import ProductSerializer, ProductListSerializer, CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products
    """
    queryset = Product.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """Check if product is available for purchase"""
        product = self.get_object()
        return Response({
            'is_in_stock': product.is_in_stock,
            'inventory_count': product.inventory_count,
            'is_sold_out': product.is_sold_out
        })

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
