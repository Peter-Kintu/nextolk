# next_tiktok/urls.py (CRITICAL FIX: Use Custom Token View)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the custom token views from your user app
from user.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView # Keep these for refresh/verify

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # MODIFIED: Use your CustomTokenObtainPairView here
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'), # Ensure verify is also here

    path('api/', include('user.urls')),  # Your existing user app URLs
    
    # IMPORTANT: Verify your e-commerce app name.
    # If your e-commerce app is actually named 'ecommerce', change 'eshop' to 'ecommerce'.
    # For example: path('api/ecommerce/', include('ecommerce.urls')),
    path('api/eshop/', include('eshop.urls')), # E-commerce URLs (adjust 'eshop' if your app is 'ecommerce')

    # If you have a separate web-based registration at the root, keep this uncommented:
    # path('register/', user_views.register, name='register'),
]

# Serve static and media files only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # NEW: Add this line for static files

