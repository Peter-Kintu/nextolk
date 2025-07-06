# user/views.py (Updated with check_like action for VideoViewSet)

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .models import Profile, Video, Comment, Like, Follow, PhoneNumberOTP # Ensure PhoneNumberOTP is imported
from .serializers import ProfileSerializer, UserSerializer, VideoSerializer, CommentSerializer, LikeSerializer, FollowSerializer, PhoneNumberOTPSerializer # Ensure PhoneNumberOTPSerializer is imported
from django.utils import timezone # Import timezone for OTP views
import random # For OTP generation

# This is a web-based view, not for the API.
# It can be kept for a web dashboard or removed if not needed.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'user/register.html', {'form': form})

# NEW: API View for User Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can view/edit profiles

    def get_queryset(self):
        # Allow users to see their own profile or public profiles
        # For simplicity, let's allow all authenticated users to see all profiles for now
        return Profile.objects.all()

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def my_profile(self, request, pk=None):
        """
        Custom action to retrieve the currently authenticated user's profile.
        """
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found for this user.'}, status=status.HTTP_404_NOT_FOUND)

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-created_at') # Order by newest first
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def following_feed(self, request):
        """
        Returns videos from users the current user is following.
        """
        followed_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        videos = Video.objects.filter(user__in=followed_users).order_by('-created_at')
        page = self.paginate_queryset(videos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def check_like(self, request, pk=None):
        """
        Checks if the authenticated user has liked a specific video.
        URL: /api/videos/{video_id}/check_like/
        """
        video = self.get_object() # pk is used to get the video object
        user = request.user
        is_liked = Like.objects.filter(user=user, video=video).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        video_id = self.kwargs['video_id']
        return Comment.objects.filter(video__id=video_id).order_by('created_at')

    def perform_create(self, serializer):
        video_id = self.kwargs['video_id']
        video = get_object_or_404(Video, id=video_id)
        serializer.save(user=self.request.user, video=video)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    user = request.user
    like_exists = Like.objects.filter(user=user, video=video).exists()

    if like_exists:
        Like.objects.filter(user=user, video=video).delete()
        video.likes_count -= 1
        video.save()
        return Response({'message': 'Video unliked.'}, status=status.HTTP_200_OK)
    else:
        Like.objects.create(user=user, video=video)
        video.likes_count += 1
        video.save()
        return Response({'message': 'Video liked.'}, status=status.HTTP_201_CREATED)

class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        following_user_id = request.data.get('following_user_id')
        if not following_user_id:
            return Response({'error': 'following_user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            following_user = User.objects.get(id=following_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User to follow not found.'}, status=status.HTTP_404_NOT_FOUND)

        follower_user = request.user

        if follower_user == following_user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        follow_exists = Follow.objects.filter(follower=follower_user, following=following_user).exists()

        if follow_exists:
            Follow.objects.filter(follower=follower_user, following=following_user).delete()

            # Update follower/following counts
            follower_user.profile.following_count = Follow.objects.filter(follower=follower_user).count()
            following_user.profile.follower_count = Follow.objects.filter(following=following_user).count()
            follower_user.profile.save()
            following_user.profile.save()

            return Response({'message': f'You are no longer following {following_user.username}.'}, status=status.HTTP_200_OK)
        else:
            Follow.objects.create(follower=follower_user, following=following_user)

            follower_user.profile.following_count = Follow.objects.filter(follower=follower_user).count()
            following_user.profile.follower_count = Follow.objects.filter(following=following_user).count()
            follower_user.profile.save()
            following_user.profile.save()

            return Response({'message': f'You are now following {following_user.username}.'}, status=status.HTTP_201_CREATED)

class IsFollowingView(APIView):
    """
    API endpoint to check if a specific user is following another user.
    URL format: /api/profiles/{profile_id}/is_followed_by/{current_user_id}/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, profile_id, current_user_id, format=None):
        target_user = get_object_or_404(User, id=profile_id)
        checker_user = get_object_or_404(User, id=current_user_id)

        # Ensure the checker_user is the authenticated user making the request
        if checker_user != request.user:
            return Response({'error': 'You can only check follow status for yourself.'}, status=status.HTTP_403_FORBIDDEN)

        is_following = Follow.objects.filter(follower=checker_user, following=target_user).exists()
        return Response({'is_following': is_following}, status=status.HTTP_200_OK)

# NEW: OTP related views
class RequestOTPView(APIView):
    """
    API endpoint to request an OTP for a given phone number.
    """
    permission_classes = [AllowAny] # Allow unauthenticated users to request OTP

    def post(self, request, format=None):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store or update the OTP in the database
        otp_instance, created = PhoneNumberOTP.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                'otp': otp,
                'created_at': timezone.now(),
                'expires_at': timezone.now() + timezone.timedelta(minutes=5) # OTP valid for 5 minutes
            }
        )

        # In a real application, you would send this OTP via SMS.
        # For now, we'll just return it in the response for testing.
        debug_message = f"DEBUG: OTP for {phone_number}: {otp}"
        print(debug_message) # Print to console for development/testing

        return Response({'message': 'OTP sent successfully.', 'otp': otp}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    """
    API endpoint to verify an OTP for a given phone number.
    """
    permission_classes = [AllowAny] # Allow unauthenticated users to verify OTP

    def post(self, request, format=None):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_instance = PhoneNumberOTP.objects.get(phone_number=phone_number, otp=otp)
        except PhoneNumberOTP.DoesNotExist:
            return Response({'error': 'Invalid OTP or phone number.'}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_instance.is_valid():
            return Response({'error': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        # If OTP is valid and not expired, you can now proceed with user authentication/registration
        # For example, find or create a user associated with this phone number.
        # This part depends on your user model and authentication flow.
        # For demonstration, we'll just indicate success.

        # Optionally, delete the OTP after successful verification to prevent reuse
        otp_instance.delete()
        return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
