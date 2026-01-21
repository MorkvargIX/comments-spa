from typing import Any, Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.comments.models import Comment
from apps.comments.serializers import CommentReadSerializer


def broadcast_comment_created(comment: Comment) -> None:
    """
    Broadcast newly created comment to all connected WebSocket clients.
    """
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
