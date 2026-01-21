from io import BytesIO
import base64
import random
import string
from typing import Any, Dict, Tuple
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageDraw, ImageFont
from rest_framework.exceptions import ValidationError

from apps.comments.constants import (
    TEXT_MIME_TYPES,
    TEXT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    IMAGE_MIME_TYPES,
    MAX_TXT_SIZE,
    MAX_IMAGE_SIZE,
)
from apps.comments.models import Comment, Attachment


# =====================
# CAPTCHA operations
# =====================

def generate_captcha_text(length: int = 5) -> str:
    """
    Generate random captcha text using latin letters and digits.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_captcha_image(text: str) -> str:
    """
    Generate captcha image and return it as base64 string.
    """
    image = Image.new("RGB", (150, 50), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    draw.text((20, 10), text, fill=(0, 0, 0), font=font)

    buffer = BytesIO()
    image.save(buffer, format='PNG')

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def store_captcha(text: str, ttl: int = 300) -> str:
    """
    Store captcha text in Redis cache and return captcha_id.
    """
    captcha_id = str(uuid.uuid4())
    cache_key = f'captcha:{captcha_id}'

    cache.set(cache_key, text, timeout=ttl)
    return captcha_id


def validate_captcha(captcha_id: str, captcha_value: str) -> None:
    """
    Validate captcha value against stored value in Redis.
    Raises ValidationError if captcha is invalid or expired.
    """
    cache_key = f'captcha:{captcha_id}'
    expected_value = cache.get(cache_key)

    if not expected_value:
        raise ValidationError('Captcha expired or not found.')

    if captcha_value.lower() != expected_value.lower():
        raise ValidationError('Invalid captcha.')

    # One-time use captcha
    cache.delete(cache_key)


# =====================
# File / attachment operations
# =====================

def process_uploaded_file(
        file: UploadedFile,
) -> Tuple[UploadedFile, Attachment.AttachmentType]:
    """
    Validate and process uploaded file.
    - validates type and size
    - resizes images if needed
    - returns processed file and attachment type
    """

    filename = file.name.lower()
    content_type = file.content_type
    size = file.size
    extension = filename.split(".")[-1]

    # TEXT FILES
    if extension in TEXT_EXTENSIONS:
        if content_type not in TEXT_MIME_TYPES:
            raise ValidationError("Invalid text file type.")

        if size > MAX_TXT_SIZE:
            raise ValidationError("Text file is too large.")

        return file, Attachment.AttachmentType.TEXT

    # IMAGE FILES
    if extension in IMAGE_EXTENSIONS:
        if content_type not in IMAGE_MIME_TYPES:
            raise ValidationError("Invalid image file type.")

        try:
            image = Image.open(file)
            image.verify()
        except Exception:
            raise ValidationError("Invalid image file.")

        file.seek(0)
        image = Image.open(file)

        if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
            image.thumbnail(MAX_IMAGE_SIZE)
            image_format = image.format or "JPEG"
            image.save(file, format=image_format)
            file.seek(0)

        return file, Attachment.AttachmentType.IMAGE

    raise ValidationError("Unsupported file type.")


# =====================
# WebSocket operations
# =====================

def broadcast_comment_created(comment: Comment) -> None:
    """
    Broadcast newly created comment to all connected WebSocket clients.
    """
    from apps.comments.serializers import CommentReadSerializer

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    payload: Dict[str, Any] = {
        'event': 'comment.created',
        'comment': CommentReadSerializer(comment).data,
    }

    async_to_sync(channel_layer.group_send)(
        'comments',
        {
            'type': 'comment.message',
            'data': payload,
        }
    )
