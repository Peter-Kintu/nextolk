# ecommerce/serializers.py

from rest_framework import serializers
from .models import Category, Product
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    Includes read-only fields for seller's username and category name,
    and a custom field for the absolute image URL.
    """
    seller_username = serializers.ReadOnlyField(source='seller.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    image_url = serializers.SerializerMethodField() # Custom field for image URL

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_username', 'category', 'category_name',
            'name', 'description', 'price', 'image', 'image_url', 'stock',
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['seller', 'created_at', 'updated_at', 'image_url']
        extra_kwargs = {
            'image': {'write_only': True, 'required': False} # Make image optional for updates
        }

    def get_image_url(self, obj):
        """
        Returns the absolute URL for the product image.
        Requires the request context to build the absolute URI.
        """
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url # Fallback if request context not available
        return None

    def create(self, validated_data):
        # The seller will be set by the view based on the authenticated user
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Handle image update separately if present
        image_file = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)
        if image_file:
            instance.image = image_file
            instance.save()
        return instance
