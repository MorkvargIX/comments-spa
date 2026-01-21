from typing import Dict, Any

import bleach
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers
from PIL import Image

from apps.comments.models import Attachment, Comment
from apps.comments.services import broadcast_comment_created
from apps.comments.services import validate_captcha


ALLOWED_TAGS = {'a', 'code', 'i', 'strong'}
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}

MAX_TXT_SIZE = 100 * 1024  # 100 KB
MAX_IMAGE_SIZE = (320, 240)

IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif')
IMAGE_MIME_TYPES = ('image/jpeg', 'image/png', 'image/gif')

TEXT_EXTENSIONS = ('txt',)
TEXT_MIME_TYPES = ('text/plain',)


class AttachmentCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Attachment
        fields = ('file',)

    def validate_file(self, file: UploadedFile) -> UploadedFile:
        filename = file.name.lower()
        content_type = file.content_type
        size = file.size

        extension = filename.split('.')[-1]

        if extension in TEXT_EXTENSIONS:
            if content_type not in TEXT_MIME_TYPES:
                raise serializers.ValidationError('Invalid text file type.')
            if size > MAX_TXT_SIZE:
                raise serializers.ValidationError('Text file is too large.')

            self._attachment_type = Attachment.AttachmentType.TEXT
            return file

        if extension in IMAGE_EXTENSIONS:
            if content_type not in IMAGE_MIME_TYPES:
                raise serializers.ValidationError('Invalid image file type.')

            try:
                image = Image.open(file)
                image.verify() # verifies image integrity; requires reopening file for further processing
            except Exception as e:
                raise serializers.ValidationError('Invalid image file.')

            file.seek(0)

            image = Image.open(file)
            if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
                image.thumbnail(MAX_IMAGE_SIZE)

                image_format = image.format or 'JPEG'
                image.save(file, format=image_format)

                file.seek(0)

            self._attachment_type = Attachment.AttachmentType.IMAGE
            return file

        raise serializers.ValidationError('Unsupported file type.')

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

    def get_url(self, obj: Attachment) -> str:
        return obj.file.url


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
            'attachments_count'
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
