        # user/signals.py
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

    logger = logging.getLogger(__name__)

        # This flag is used to prevent infinite loops when saving the Video model inside the signal.
        # When the signal saves the model, it temporarily sets this flag to True,
        # so the next post_save signal triggered by that save operation will ignore it.
    _STILL_SAVING_VIDEO = threading.local()
    _STILL_SAVING_VIDEO.value = False

    @receiver(post_save, sender=Video)
    def transcode_video_on_upload(sender, instance, created, **kwargs):
            """
            Signal to transcode uploaded videos to a web-friendly H.264/AAC MP4 format.
            This runs in a separate thread to avoid blocking the main request,
            but for production, a proper task queue (e.g., Celery) is recommended.
            """
            # Prevent infinite loop: If this signal is triggered by a save operation
            # initiated by this very signal, then exit.
        if _STILL_SAVING_VIDEO.value:
            return

        if created: # Only transcode new videos
                # Check if the video file exists and is not already in the desired format (optional, but good)
                # For simplicity, we'll assume all new uploads need transcoding.
                
                # Run transcoding in a separate thread to avoid blocking the HTTP response
                # NOTE: For a high-traffic production app, use a proper async task queue (e.g., Celery)
                # This threading approach is for demonstration/small scale.
            thread = threading.Thread(target=_transcode_and_update_video, args=(instance.id,))
            thread.start()

    def _transcode_and_update_video(video_id):
            """
            Internal function to handle the video transcoding and model update.
            Runs in a separate thread.
            """
        try:
                # Re-fetch the instance within the thread to ensure it's up-to-date
            video_instance = Video.objects.get(id=video_id)
            original_file_path = video_instance.video_file.path
            original_file_name = os.path.basename(original_file_path)
                
                # Define output path and name
                # We'll save the transcoded file in the same directory but with a new name
                # to avoid conflicts and indicate it's the processed version.
                # Example: 'videos/original_name.mp4' -> 'videos/original_name_transcoded.mp4'
            base_name, ext = os.path.splitext(original_file_name)
            transcoded_file_name = f"{base_name}_transcoded.mp4"
            transcoded_file_path = os.path.join(settings.MEDIA_ROOT, 'videos', transcoded_file_name)
                
                # Ensure the output directory exists
            os.makedirs(os.path.dirname(transcoded_file_path), exist_ok=True)

            logger.info(f"Starting transcoding for video ID {video_id}: {original_file_path}")
            logger.info(f"Output path: {transcoded_file_path}")

                # FFmpeg command to transcode to H.264/AAC MP4
                # -y: overwrite output file if it exists
                # -c:v libx264: video codec to H.264
                # -c:a aac: audio codec to AAC
                # -strict -2: required for experimental AAC encoder (older ffmpeg versions)
                # -b:v 1M: video bitrate (adjust as needed for quality vs file size)
                # -preset veryfast: faster encoding, larger file size (use 'medium' for better quality)
                # -movflags +faststart: optimizes for web streaming
                
                # Use ffmpeg-python to run the command
            (
                ffmpeg
                .input(original_file_path)
                .output(transcoded_file_path, vcodec='libx264', acodec='aac', strict='experimental', movflags='faststart', preset='veryfast', crf=23)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
                
            logger.info(f"Finished transcoding for video ID {video_id}.")

                # Update the video_file field to point to the new transcoded file
                # We need to use default_storage to save the file correctly in Django's FileField
            with open(transcoded_file_path, 'rb') as f:
                content_file = ContentFile(f.read(), name=transcoded_file_name)
                    
                    # Temporarily set the flag to prevent infinite recursion
                _STILL_SAVING_VIDEO.value = True
                try:
                    video_instance.video_file.save(transcoded_file_name, content_file, save=False)
                    video_instance.save(update_fields=['video_file'])
                    logger.info(f"Video ID {video_id} updated with transcoded file: {video_instance.video_file.url}")
                finally:
                    _STILL_SAVING_VIDEO.value = False # Always reset the flag

                # Delete the original uploaded file to save space
            if default_storage.exists(original_file_path) and original_file_path != transcoded_file_path:
                default_storage.delete(original_file_path)
                logger.info(f"Original video file deleted: {original_file_path}")

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error during transcoding for video ID {video_id}: {e.stderr.decode()}", exc_info=True)
        except Exception as e:
            logger.error(f"Error during video transcoding for video ID {video_id}: {e}", exc_info=True)

        