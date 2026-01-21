from typing import Any, Dict

from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        """
        Called when a WebSocket connection is opened.

        Subscribes the current socket channel to the `comments` group
        to receive broadcast events related to comments.
        """
        self.group_name = "comments"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        """
        Called when a WebSocket connection is closed.

        Removes the socket channel from the `comments` group.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def comment_message(self, event: Dict[str, Any]) -> None:
        """
        Handles `comment.message` events sent via the channel layer.

        Expected event structure:
        {
            "type": "comment.message",
            "data": { ... }  # Serialized comment payload
        }

        The event is delivered by:
            channel_layer.group_send(
                "comments",
                {
                    "type": "comment.message",
                    "data": payload,
                }
            )
        """
        await self.send_json(event["data"])
