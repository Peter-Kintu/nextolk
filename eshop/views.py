# ecommerce/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.shortcuts import get_object_or_404

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows categories to be viewed.
    Only GET (list and retrieve) operations are allowed.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] # Categories can be viewed by anyone

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be created, viewed, updated, or deleted.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can manage products

    def get_queryset(self):
        """
        Optionally restricts the returned products to a given seller (user).
        """
        queryset = Product.objects.all().order_by('-created_at')
        seller_id = self.request.query_params.get('seller_id', None)
        if seller_id is not None:
            queryset = queryset.filter(seller__id=seller_id)
        return queryset

    def perform_create(self, serializer):
        """
        Sets the seller of the product to the authenticated user.
        """
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        """
        Ensures only the seller can update their own product.
        """
        product = self.get_object()
        if product.seller != self.request.user:
            return Response(
                {"detail": "You do not have permission to edit this product."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Ensures only the seller can delete their own product.
        """
        if instance.seller != self.request.user:
            return Response(
                {"detail": "You do not have permission to delete this product."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    def get_serializer_context(self):
        """
        Passes the request context to the serializer for building absolute URLs.
        """
        return {'request': self.request}
