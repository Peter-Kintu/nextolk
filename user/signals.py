    # user/signals.py (UPDATED: S3 Compatibility for Transcoding)

    import os
    import ffmpeg
    from django.db.models.signals import post_save
    from django.dispatch import receiver
    from .models import Video
    from django.conf import settings
    import threading
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import logging
    import tempfile # NEW
    import shutil # NEW

    logger = logging.getLogger(__name__)

    _STILL_SAVING_VIDEO = threading.local()
    _STILL_SAVING_VIDEO.value = False

    @receiver(post_save, sender=Video)
    def transcode_video_on_upload(sender, instance, created, **kwargs):
        if _STILL_SAVING_VIDEO.value:
            return

        # Only transcode if it's a new video and it's not already an S3 URL (meaning it's a new upload to local storage first)
        # Or if you want to force re-transcoding for existing S3 files, adjust this logic.
        if created and not instance.video_file.url.startswith('http'): # Check if it's a local path
            thread = threading.Thread(target=_transcode_and_update_video, args=(instance.id,))
            thread.start()

    def _transcode_and_update_video(video_id):
        temp_dir = None # Initialize temp_dir
        try:
            video_instance = Video.objects.get(id=video_id)
            
            # Create a temporary directory to store the downloaded and transcoded files
            temp_dir = tempfile.mkdtemp()
            original_local_path = os.path.join(temp_dir, os.path.basename(video_instance.video_file.name))
            transcoded_local_path = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(video_instance.video_file.name))[0]}_transcoded.mp4")

            logger.info(f"Downloading original video {video_instance.video_file.name} to {original_local_path}")
            # Download the original file from S3 (or local storage) to a temporary local path
            with default_storage.open(video_instance.video_file.name, 'rb') as s3_file:
                with open(original_local_path, 'wb') as local_file:
                    for chunk in s3_file.chunks():
                        local_file.write(chunk)
            logger.info(f"Original video downloaded to {original_local_path}")

            logger.info(f"Starting transcoding for video ID {video_id}: {original_local_path}")
            logger.info(f"Output path: {transcoded_local_path}")

            (
                ffmpeg
                .input(original_local_path)
                .output(transcoded_local_path, vcodec='libx264', acodec='aac', strict='experimental', movflags='faststart', preset='veryfast', crf=23)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            logger.info(f"Finished transcoding for video ID {video_id}.")

            # Upload the transcoded file back to S3
            with open(transcoded_local_path, 'rb') as f:
                content_file = ContentFile(f.read(), name=os.path.basename(transcoded_local_path))
                
                _STILL_SAVING_VIDEO.value = True
                try:
                    # Save the new transcoded file to S3
                    video_instance.video_file.save(os.path.basename(transcoded_local_path), content_file, save=False)
                    video_instance.save(update_fields=['video_file'])
                    logger.info(f"Video ID {video_id} updated with transcoded file: {video_instance.video_file.url}")
                finally:
                    _STILL_SAVING_VIDEO.value = False

            # Delete the original file from S3
            default_storage.delete(video_instance.video_file.name)
            logger.info(f"Original video file deleted from storage: {video_instance.video_file.name}")

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error during transcoding for video ID {video_id}: {e.stderr.decode()}", exc_info=True)
        except Exception as e:
            logger.error(f"Error during video transcoding for video ID {video_id}: {e}", exc_info=True)
        finally:
            # Clean up the temporary directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Temporary directory {temp_dir} removed.")

    