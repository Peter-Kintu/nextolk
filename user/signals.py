# user/signals.py (UPDATED: Added Debug Logging for Cloudinary Upload)

import os
# import ffmpeg # Ensure this is commented out if not using local FFmpeg
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video, Profile
from django.conf import settings
import threading
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import tempfile
import shutil
import cloudinary.uploader

logger = logging.getLogger(__name__)

_STILL_SAVING_VIDEO = threading.local()
_STILL_SAVING_VIDEO.value = False

@receiver(post_save, sender=Video)
def upload_video_to_cloudinary(sender, instance, created, **kwargs):
    """
    Signal to upload new video files to Cloudinary.
    This runs in a separate thread to avoid blocking the main request.
    """
    if _STILL_SAVING_VIDEO.value:
        return

    # Only process if it's a new video and the video_file is a local file
    # (i.e., not already a Cloudinary URL). CloudinaryField saves to default_storage first.
    if created and instance.video_file and not instance.video_file.url.startswith('http'):
        try:
            # Read the file content from default_storage (which is where CloudinaryField puts it initially)
            with default_storage.open(instance.video_file.name, 'rb') as f:
                file_content = f.read()
            
            # Log file details before attempting upload
            logger.debug(f"Video upload signal: Processing file '{instance.video_file.name}', size: {len(file_content)} bytes")
            
            thread = threading.Thread(target=_upload_and_update_video, args=(instance.id, file_content, instance.video_file.name))
            thread.start()
        except Exception as e:
            logger.error(f"Error reading video file for Cloudinary upload: {e}", exc_info=True)


@receiver(post_save, sender=Profile)
def upload_profile_picture_to_cloudinary(sender, instance, created, **kwargs):
    """
    Signal to upload new profile pictures to Cloudinary.
    """
    if _STILL_SAVING_VIDEO.value:
        return

    # Only process if it's a new profile picture and it's a local file
    if instance.profile_picture and not instance.profile_picture.url.startswith('http'):
        try:
            with default_storage.open(instance.profile_picture.name, 'rb') as f:
                file_content = f.read()

            # Log file details before attempting upload
            logger.debug(f"Profile picture upload signal: Processing file '{instance.profile_picture.name}', size: {len(file_content)} bytes")

            thread = threading.Thread(target=_upload_and_update_profile_picture, args=(instance.id, file_content, instance.profile_picture.name))
            thread.start()
        except Exception as e:
            logger.error(f"Error reading profile picture file for Cloudinary upload: {e}", exc_info=True)


def _upload_and_update_video(video_id, file_content, file_name):
    """
    Internal function to handle video upload to Cloudinary and model update.
    Runs in a separate thread.
    """
    try:
        video_instance = Video.objects.get(id=video_id)
        
        logger.info(f"Uploading video {file_name} for video ID {video_id} to Cloudinary.")
        
        # Explicitly set resource_type to "video"
        upload_result = cloudinary.uploader.upload(
            file_content,
            resource_type="video",
            public_id=f"nextolke_videos/{os.path.splitext(file_name)[0]}",
            folder="nextolke_videos",
            eager=[
                {"width": 640, "height": 480, "crop": "limit", "format": "mp4", "quality": "auto"},
                {"width": 320, "height": 240, "crop": "limit", "format": "webm", "quality": "auto"}
            ],
            invalidate=True
        )
        
        logger.info(f"Cloudinary upload result for video ID {video_id}: {upload_result}")

        _STILL_SAVING_VIDEO.value = True
        try:
            video_instance.video_file = upload_result['public_id']
            video_instance.save(update_fields=['video_file'])
            logger.info(f"Video ID {video_id} updated with Cloudinary public ID: {video_instance.video_file.public_id}")
        finally:
            _STILL_SAVING_VIDEO.value = False

        # Delete the temporary local file that Django's CloudinaryField might have saved
        if default_storage.exists(video_instance.video_file.name):
            default_storage.delete(video_instance.video_file.name)
            logger.info(f"Local temporary video file deleted: {video_instance.video_file.name}")

    except Exception as e:
        logger.error(f"Error during video upload to Cloudinary for video ID {video_id}: {e}", exc_info=True)

def _upload_and_update_profile_picture(profile_id, file_content, file_name):
    """
    Internal function to handle profile picture upload to Cloudinary and model update.
    Runs in a separate thread.
    """
    try:
        profile_instance = Profile.objects.get(id=profile_id)
        
        logger.info(f"Uploading profile picture {file_name} for profile ID {profile_id} to Cloudinary.")

        # Explicitly set resource_type to "image"
        upload_result = cloudinary.uploader.upload(
            file_content,
            resource_type="image", # Ensure this is 'image' for profile pictures
            public_id=f"nextolke_profile_pics/{os.path.splitext(file_name)[0]}",
            folder="nextolke_profile_pics",
            eager=[
                {"width": 200, "height": 200, "crop": "fill", "gravity": "face", "format": "jpg"}
            ],
            invalidate=True
        )
        
        logger.info(f"Cloudinary upload result for profile ID {profile_id}: {upload_result}")

        _STILL_SAVING_VIDEO.value = True
        try:
            profile_instance.profile_picture = upload_result['public_id']
            profile_instance.save(update_fields=['profile_picture'])
            logger.info(f"Profile ID {profile_id} updated with Cloudinary public ID: {profile_instance.profile_picture.public_id}")
        finally:
            _STILL_SAVING_VIDEO.value = False

        # Delete the temporary local file if it was saved locally first
        if default_storage.exists(profile_instance.profile_picture.name):
            default_storage.delete(profile_instance.profile_picture.name)
            logger.info(f"Local temporary profile picture file deleted: {profile_instance.profile_picture.name}")

    except Exception as e:
        logger.error(f"Error during profile picture upload to Cloudinary for profile ID {profile_id}: {e}", exc_info=True)
