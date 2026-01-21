from io import BytesIO
import base64
import random
import string
from typing import Any, Dict
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from PIL import Image, ImageDraw, ImageFont
from rest_framework.exceptions import ValidationError

from apps.comments.models import Comment


# CAPTCHA operations
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


# WS operations

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
