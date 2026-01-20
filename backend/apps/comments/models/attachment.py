from django.db import models

from apps.comments.models.comment import Comment
from apps.core.models.mixins import AuditMixin


class Attachment(AuditMixin):
    class AttachmentType(models.TextChoices):
        IMAGE = 'image', 'Image'
        TEXT = 'text', 'Text file'

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments')

    file = models.FileField(upload_to='attachments/',)
    type = models.CharField(max_length=10, choices=AttachmentType.choices)

    original_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'{self.type} attachment for comment #{self.comment_id}'
