# user/views.py (UPDATED: Added CustomTokenObtainPairView)

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .models import Profile, Video, Comment, Like, Follow, PhoneNumberOTP
from .serializers import ProfileSerializer, UserSerializer, VideoSerializer, CommentSerializer, LikeSerializer, FollowSerializer, PhoneNumberOTPSerializer
from django.utils import timezone
import random

# Import the custom serializer
from .serializers import CustomTokenObtainPairSerializer # Import this
from rest_framework_simplejwt.views import TokenObtainPairView # Import the base view

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

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

# --- NEW: Custom Token Obtain Pair View ---
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Customized JWT Token Obtain Pair View to include user_id and username in the response.
    """
    serializer_class = CustomTokenObtainPairSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can access profiles

    def get_queryset(self):
        """
        Optionally restricts the returned profiles to a given user,
        by filtering against a `user_id` query parameter in the URL.
        """
        queryset = Profile.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)
        return queryset

    def perform_create(self, serializer):
        # This is typically handled by a signal (create_user_profile)
        # but if you create profiles directly, ensure user is set.
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """
        Custom partial update to handle profile picture and bio updates.
        """
        instance = self.get_object()
        # Ensure the user is updating their own profile
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows videos to be viewed or edited.
    """
    queryset = Video.objects.all().order_by('-created_at') # Order by newest first
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='following_feed')
    def following_feed(self, request):
        """
        Get videos from users that the current user is following.
        """
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
        videos = Video.objects.filter(user__in=following_users).order_by('-created_at')
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='check_like')
    def check_like(self, request, pk=None):
        """
        Check if the current user has liked a specific video.
        """
        video = get_object_or_404(Video, pk=pk)
        user = request.user
        is_liked = Like.objects.filter(video=video, user=user).exists()
        return Response({'is_liked': is_liked})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, video_id):
    """
    API endpoint to toggle a like on a video.
    """
    video = get_object_or_404(Video, id=video_id)
    user = request.user

    try:
        like = Like.objects.get(video=video, user=user)
        like.delete()
        video.likes_count -= 1
        video.save()
        return Response({'status': 'unliked', 'likes_count': video.likes_count}, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        Like.objects.create(video=video, user=user)
        video.likes_count += 1
        video.save()
        return Response({'status': 'liked', 'likes_count': video.likes_count}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned comments to a given video,
        by filtering against a `video_id` in the URL.
        """
        queryset = Comment.objects.all()
        video_id = self.kwargs.get('video_id')
        if video_id is not None:
            queryset = queryset.filter(video__id=video_id)
        return queryset

    def perform_create(self, serializer):
        video_id = self.kwargs.get('video_id')
        video = get_object_or_404(Video, id=video_id)
        serializer.save(user=self.request.user, video=video)
        video.comments_count += 1
        video.save()

    def perform_destroy(self, instance):
        video = instance.video
        instance.delete()
        video.comments_count -= 1
        video.save()


class FollowView(APIView):
    """
    API endpoint to toggle follow/unfollow a user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        following_user_id = request.data.get('following_id')
        if not following_user_id:
            return Response({'error': 'following_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            following_user = User.objects.get(id=following_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User to follow not found.'}, status=status.HTTP_404_NOT_FOUND)

        follower_user = request.user

        if follower_user == following_user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            follow_instance = Follow.objects.get(follower=follower_user, following=following_user)
            follow_instance.delete()
            # Update follower/following counts
            follower_profile = Profile.objects.get(user=follower_user)
            following_profile = Profile.objects.get(user=following_user)
            follower_profile.following_count -= 1
            following_profile.follower_count -= 1
            follower_profile.save()
            following_profile.save()
            return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            Follow.objects.create(follower=follower_user, following=following_user)
            # Update follower/following counts
            follower_profile = Profile.objects.get(user=follower_user)
            following_profile = Profile.objects.get(user=following_user)
            follower_profile.following_count += 1
            following_profile.follower_count += 1
            follower_profile.save()
            following_profile.save()
            return Response({'status': 'followed'}, status=status.HTTP_201_CREATED)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found for user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IsFollowingView(APIView):
    """
    API endpoint to check if a current user is following a specific profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, profile_id, current_user_id, format=None):
        try:
            target_profile = Profile.objects.get(id=profile_id)
            current_user = User.objects.get(id=current_user_id)
        except Profile.DoesNotExist:
            return Response({'error': 'Target profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Current user not found.'}, status=status.HTTP_404_NOT_FOUND)

        is_following = Follow.objects.filter(follower=current_user, following=target_profile.user).exists()
        return Response({'is_following': is_following}, status=status.HTTP_200_OK)


class RequestOTPView(APIView):
    """
    API endpoint to request an OTP for phone number verification.
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP with expiration (overwrite if existing for same number)
        PhoneNumberOTP.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                'otp': otp,
                'expires_at': timezone.now() + timezone.timedelta(minutes=5)
            }
        )

        # In a real application, you would send this OTP via an SMS gateway
        # debug_print_otp = f"OTP for {phone_number}: {otp}" # For debugging purposes only
        # print(debug_print_otp) # Print to console for development

        return Response({'message': 'OTP sent successfully.', 'otp': otp}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    API endpoint to verify an OTP for a given phone number.
    """
    permission_classes = [AllowAny]

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


# NEW: View to get the current authenticated user's profile
class CurrentUserProfileView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve the profile of the currently authenticated user.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Ensure the user has a profile, create one if not (though signal should handle this)
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

