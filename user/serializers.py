# user/serializers.py (CRITICAL BACKEND FIX: Include user_id and username in Token Response)

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Video, Comment, Like, Follow, PhoneNumberOTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # Import the base serializer

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, including a writable 'create' method
    for user registration to hash the password.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'] # Password will be hashed by create_user
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    # Add a field for the profile picture URL
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'profile_picture', 'profile_picture_url', 'follower_count', 'following_count', 'created_at']
        read_only_fields = ['follower_count', 'following_count', 'created_at']

    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            # Check if request context is available for absolute URL
            if 'request' in self.context:
                return self.context['request'].build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url # Fallback if request context not available
        return None

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.
    Includes user_id, user_username, user_profile_picture, hashtags, audio_name, and applied_filters.
    """
    user_id = serializers.ReadOnlyField(source='user.id') # Explicitly add user_id
    user_username = serializers.ReadOnlyField(source='user.username') # Explicitly add user_username
    user_profile_picture = serializers.SerializerMethodField() # Add profile picture URL

    class Meta:
        model = Video
        fields = [
            'id', 'user', 'user_id', 'user_username', 'user_profile_picture',
            'video_file', 'caption', 'likes_count', 'comments_count',
            'created_at', 'hashtags', 'audio_name', 'applied_filters', 'is_live'
        ]
        read_only_fields = ['user', 'likes_count', 'comments_count', 'created_at', 'user_id', 'user_username', 'user_profile_picture']

    def get_user_profile_picture(self, obj):
        # Get the profile picture URL from the associated Profile model
        if hasattr(obj.user, 'profile') and obj.user.profile.profile_picture:
            if 'request' in self.context:
                return self.context['request'].build_absolute_uri(obj.user.profile.profile_picture.url)
            return obj.user.profile.profile_picture.url
        return None

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user', 'text', 'created_at']
        read_only_fields = ['user', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model.
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'video', 'user']
        read_only_fields = ['user']

class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for the Follow model.
    """
    follower = serializers.ReadOnlyField(source='follower.username')
    following = serializers.ReadOnlyField(source='following.username')

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'following', 'created_at']

class PhoneNumberOTPSerializer(serializers.ModelSerializer):
    """
    Serializer for the PhoneNumberOTP model.
    """
    class Meta:
        model = PhoneNumberOTP
        fields = ['phone_number', 'otp', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']

# NEW: Custom Token Obtain Pair Serializer to include user_id and username
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT TokenObtainPairSerializer to include user_id and username
    in the response data.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user_id and username to the response data
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        return data
