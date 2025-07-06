# user/models.py (Re-updated to add null=True for JSONFields)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Video(models.Model):
    """
    Model to store video information, including metadata from the video editor.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    video_file = models.FileField(upload_to='videos/')
    caption = models.TextField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW: Fields for video editing metadata
    # Using JSONField to store lists of strings for hashtags and applied_filters
    # Add null=True here
    hashtags = models.JSONField(default=list, blank=True, null=True)
    audio_name = models.CharField(max_length=255, blank=True, null=True)
    applied_filters = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f'Video by {self.user.username} - {self.caption[:30]}'

class Comment(models.Model):
    """
    Model to store comments on videos.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.video.caption[:20]}'

class Like(models.Model):
    """
    Model to store likes on videos.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only like a video once
        unique_together = ('video', 'user')

    def __str__(self):
        return f'{self.user.username} likes {self.video.caption[:20]}'

class Follow(models.Model):
    """
    Model to represent a follower-following relationship between users.
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
