# ecommerce/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Model for product categories (e.g., 'Fashion', 'Electronics', 'Art').
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Model for individual products listed for sale.
    """
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.seller.username}"

    @property
    def image_url(self):
        """
        Returns the absolute URL for the product image.
        This property is useful for serializers to get the full URL.
        """
        if self.image:
            return self.image.url
        return None

# TODO: Future models for a complete e-commerce system:
# - Order (user, total_amount, status, created_at)
# - OrderItem (order, product, quantity, price_at_purchase)
# - ShippingAddress (user, address_details)
# - Payment (order, amount, status, transaction_id)
# - Review (product, user, rating, comment)
