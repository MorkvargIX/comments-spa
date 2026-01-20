from typing import Union

import bleach
from rest_framework import serializers
from apps.comments.models import Comment


ALLOWED_TAGS = {'a', 'code', 'i', 'strong'}
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'user_name',
            'email',
            'home_page',
            'body',
            'parent',
        )

    def validate_body(self, value: str) -> str:
        """
        Sanitize HTML to prevent XSS.
        Allow only whitelisted tags.
        """
        return bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
        )


class CommentReadSerializer(serializers.ModelSerializer):
    replies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        read_only_fields = ("id", "created_at")
        fields = (
            'id',
            'user_name',
            'email',
            'home_page',
            'body',
            'created_at',
            'replies_count'
        )

