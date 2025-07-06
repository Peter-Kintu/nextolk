# users/urls.py (updated to fix FollowView as_as_view() typo)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profile')
router.register(r'videos', views.VideoViewSet, basename='video')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # NEW: API registration endpoint
    path('register/', views.RegisterView.as_view(), name='api_register'),

    # NEW: JWT Authentication Endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('', include(router.urls)),
    path('videos/<int:video_id>/toggle_like/', views.toggle_like, name='toggle_like'),
    path('follow/', views.FollowView.as_view(), name='follow_toggle'), # Corrected: as_view()

    # Paths for CommentViewSet, nested under videos (if you prefer this nesting)
    # If you registered comments with the router above, you might not need these specific paths
    path('videos/<int:video_id>/comments/',
         views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='video-comments-list-create'),
    path('videos/<int:video_id>/comments/<int:pk>/',
         views.CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='video-comments-detail'),

    # NEW: URL for checking if a user is following another
    path('profiles/<int:profile_id>/is_followed_by/<int:current_user_id>/',
         views.IsFollowingView.as_view(), name='is_following'),

    # NEW: URL for fetching the following feed (videos from followed users)
    path('videos/following_feed/', views.VideoViewSet.as_view({'get': 'following_feed'}), name='following_feed'),

    # NEW: URLs for Phone Number OTP
    path('request-otp/', views.RequestOTPView.as_view(), name='request_otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
]
