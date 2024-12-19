from PIL import Image
from django.core.exceptions import ValidationError


def resize_image(image_path, max_width=200, max_height=100):
    """Resize an image to the specified dimensions."""
    image = Image.open(image_path)
    # Use Image.Resampling.LANCZOS as the replacement for Image.ANTIALIAS
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    image.save(image_path)

def validate_video_size(video_file, max_size=10 * 1024 * 1024):
    """Validate that the video file does not exceed the max size."""
    if video_file.size > max_size:
        raise ValidationError(f"The video file is too large (maximum size is {max_size // (1024 * 1024)}MB).")



def create_notification(recipient, sender, content, url):
    from .models import Notification  # Local import to avoid circular dependency
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        content=content,
        url=url,
    )
