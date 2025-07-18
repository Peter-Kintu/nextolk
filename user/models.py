# user/models.py (UPDATED: Fixed f-string syntax error in Profile.__str__)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.conf import settings # Import settings to access CLOUDINARY_CLOUD_NAME

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    # Explicitly set resource_type to 'image'
    profile_picture = CloudinaryField('image', blank=True, null=True, resource_type='image')
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # CORRECTED: Removed the extra '}' which caused the SyntaxError
        return f'{self.user.username} Profile'

class Video(models.Model):
    """
    Model to store video information, including metadata from the video editor.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    # Explicitly set resource_type to 'video'
    video_file = CloudinaryField('video', resource_type='video')
    caption = models.TextField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW: Fields for video editing metadata
    hashtags = models.JSONField(default=list, blank=True, null=True) # Store list of strings
    audio_name = models.CharField(max_length=255, blank=True, null=True) # Name of applied audio track
    applied_filters = models.JSONField(default=list, blank=True, null=True) # List of applied filter names
    is_live = models.BooleanField(default=False) # NEW FIELD: To indicate if the video is a live stream

    def __str__(self):
        return f'Video by {self.user.username} - {self.caption[:30]}'

    class Meta:
        ordering = ['-created_at'] # Order videos by newest first

    def get_full_cloudinary_url(self):
        """
        Constructs the full Cloudinary URL for the video file.
        This is useful for direct linking and debugging.
        Assumes video_file stores the public ID (e.g., 'nextolke_videos/my_video').
        """
        if self.video_file:
            # CloudinaryField.url already gives the full URL with version and format,
            # but sometimes you might want a more controlled URL or if the field
            # stores only the public ID string.
            # If video_file is a CloudinaryField, its .url property is already the full URL.
            # If it's storing just the public ID string, you'd construct it like this:
            # return f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/{self.video_file}"
            return self.video_file.url # Use the .url property of CloudinaryField
        return None


class Comment(models.Model):
    """
    Model for comments on videos.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Order comments by oldest first


class Like(models.Model):
    """
    Model for likes on videos.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user') # A user can only like a video once

    def __str__(self):
        return f'Like by {self.user.username} on {self.video.caption[:20]}'


class Follow(models.Model):
    """
    Model to represent a user following another user.
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relationships')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relationships')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only follow another user once
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'

# --- NEW MODEL FOR PHONE NUMBER OTP ---
class PhoneNumberOTP(models.Model):
    """
    Model to store One-Time Passwords for phone number verification.
    """
    phone_number = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=6) # Typically 4-6 digits
    created_at = models.DateTimeField(auto_now_add=True)
    # OTP valid for 5 minutes (adjust as needed)
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=5))

    def is_valid(self):
        """Checks if the OTP is still valid based on its expiration time."""
        return timezone.now() < self.expires_at

    def __str__(self):
        return f'OTP for {self.phone_number}: {self.otp}'

# Signal to create a Profile for a new User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
