# user/serializers.py (Updated with user_id, user_profile_picture, hashtags, audio_name, applied_filters in VideoSerializer)

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Video, Comment, Like, Follow, PhoneNumberOTP # Ensure PhoneNumberOTP is imported

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
        fields = ['user', 'bio', 'profile_picture', 'profile_picture_url', 'follower_count', 'following_count']
        read_only_fields = ['follower_count', 'following_count']

    def get_profile_picture_url(self, obj):
        # Return the absolute URL for the profile picture
        # Assumes request context is passed to the serializer for build_absolute_uri
        if obj.profile_picture:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url # Fallback if request context not available
        return None

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model, now including the user's
    username, user ID, profile picture, hashtags, audio name, and applied filters.
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    user_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'user', 'user_username', 'user_id', 'user_profile_picture',
            'video_file', 'caption', 'likes_count', 'comments_count',
            'created_at', 'hashtags', 'audio_name', 'applied_filters'
        ]
        read_only_fields = ['user', 'likes_count', 'comments_count', 'created_at']

    def get_user_profile_picture(self, obj):
        # Return the absolute URL for the user's profile picture
        if obj.user.profile.profile_picture:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.user.profile.profile_picture.url)
            return obj.user.profile.profile_picture.url # Fallback if request context not available
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
        fields = ['id', 'phone_number', 'otp', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']
