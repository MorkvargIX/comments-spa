from typing import Dict, Any

import bleach
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from apps.comments.constants import ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from apps.comments.models import Attachment, Comment
from apps.comments.services import broadcast_comment_created, validate_captcha, process_uploaded_file


class AttachmentCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Attachment
        fields = ('file',)

    def validate_file(self, file: UploadedFile) -> UploadedFile:
        processed_file, attachment_type = process_uploaded_file(file)
        self._attachment_type = attachment_type
        return processed_file

    def create(self, validated_data: Dict[str, Any]) -> Attachment:
        file = validated_data['file']

        return Attachment.objects.create(
            comment=self.context['comment'],
            file=file,
            type=self._attachment_type,
            original_name=file.name
        )


class AttachmentReadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = (
            'id',
            'type',
            'original_name',
            'url',
        )

    def get_url(self, obj):
        path = reverse('attachment-detail', args=[obj.id])
        return f'{settings.SITE_URL}{path}'


class CommentCreateSerializer(serializers.ModelSerializer):
    captcha_id = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            'user_name',
            'email',
            'home_page',
            'body',
            'parent',
            'files',
            'captcha_id',
            'captcha_value',
        )

    def validate(self, attrs):
        validate_captcha(
            captcha_id=attrs.pop('captcha_id'),
            captcha_value=attrs.pop('captcha_value'),
        )
        return attrs

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

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Comment:
        uploaded_files = validated_data.pop('files', [])

        comment = Comment.objects.create(**validated_data)

        for uploaded_file in uploaded_files:
            attachment_serializer = AttachmentCreateSerializer(
                data={'file': uploaded_file},
                context={'comment': comment},
            )
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()

        # WebSocket broadcast (after successful DB + files save)
        broadcast_comment_created(comment)
        return comment


class CommentReadSerializer(serializers.ModelSerializer):
    replies_count = serializers.IntegerField(read_only=True)
    attachments_count = serializers.IntegerField(read_only=True)
    attachments = AttachmentReadSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        read_only_fields = ('id', 'created_at')
        fields = (
            'id',
            'user_name',
            'email',
            'home_page',
            'body',
            'created_at',
            'replies_count',
            'attachments_count',
            'attachments',
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    attachments = AttachmentReadSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'user_name',
            'email',
            'home_page',
            'body',
            'created_at',
            'attachments',
        )
