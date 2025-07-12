# user/admin.py (Updated to register Follow model and PhoneNumberOTP model, and enhance Video display)
from django.contrib import admin
from django.utils.html import format_html # Import format_html for rendering HTML links
from .models import Profile, Video, Comment, Like, Follow, PhoneNumberOTP # Import the new PhoneNumberOTP model
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    """
    list_display = ('user', 'follower_count', 'following_count', 'created_at')
    search_fields = ('user__username', 'bio')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Video model.
    """
    list_display = ('id', 'user', 'caption', 'video_file', 'cloudinary_video_url', 'likes_count', 'comments_count', 'created_at', 'audio_name', 'applied_filters') # Added video_file and cloudinary_video_url
    search_fields = ('user__username', 'caption', 'hashtags', 'audio_name', 'applied_filters') # Added new fields
    list_filter = ('created_at', 'applied_filters') # Added new field
    readonly_fields = ('created_at', 'likes_count', 'comments_count', 'cloudinary_video_url') # Make cloudinary_video_url read-only
    raw_id_fields = ('user',)

    def cloudinary_video_url(self, obj):
        """
        Custom method to display a clickable link to the Cloudinary video.
        """
        if obj.video_file:
            # Use obj.video_file.url directly as CloudinaryField's .url property
            # already provides the full URL.
            return format_html('<a href="{}" target="_blank">{}</a>', obj.video_file.url, "View Video")
        return "No video file"
    
    cloudinary_video_url.short_description = "Cloudinary URL" # Column header name


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Comment model.
    """
    list_display = ('id', 'user', 'video', 'text', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'video')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Like model.
    """
    list_display = ('id', 'user', 'video', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'video')

# --- NEW: Admin configuration for the Follow model ---
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Follow model.
    """
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
    raw_id_fields = ('follower', 'following')
    readonly_fields = ('created_at',)

# --- NEW: Admin configuration for the PhoneNumberOTP model ---
@admin.register(PhoneNumberOTP)
class PhoneNumberOTPAdmin(admin.ModelAdmin):
    """
    Admin configuration for the PhoneNumberOTP model.
    """
    list_display = ('phone_number', 'otp', 'created_at', 'expires_at', 'is_valid')
    search_fields = ('phone_number',)
    list_filter = ('created_at', 'expires_at')
    readonly_fields = ('created_at', 'expires_at', 'is_valid') # OTP should not be manually editable after creation
