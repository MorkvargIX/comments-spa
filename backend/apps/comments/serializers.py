import bleach
from rest_framework import serializers
from PIL import Image

from apps.comments.models import Attachment, Comment


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

    def validate_file(self, file):
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

    def create(self, validated_data):
        file = validated_data['file']

        return Attachment.objects.create(
            comment=self.context['comment'],
            file=file,
            type=self._attachment_type,
            original_name=file.name
        )


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
        read_only_fields = ('id', 'created_at')
        fields = (
            'id',
            'user_name',
            'email',
            'home_page',
            'body',
            'created_at',
            'replies_count'
        )

