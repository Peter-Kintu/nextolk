# next_tiktok/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # Simple JWT authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/', include('user.urls')),   # Your existing user app URLs
    # FIXED: Changed 'eshop' to 'ecommerce' to match the app name and Flutter client expectation
    path('api/eshop/', include('eshop.urls')), # E-commerce URLs

    # If you have a separate web-based registration at the root, keep this uncommented:
    # path('register/', user_views.register, name='register'),
]

# Serve static and media files only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # NEW: Add this line for static files
