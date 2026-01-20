from django.db import models

from apps.core.models.mixins import AuditMixin


class Comment(AuditMixin):
    user_name = models.CharField(max_length=255)
    email = models.EmailField()
    home_page = models.URLField(blank=True)
    body = models.TextField()

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        db_index=True,
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f"Comment #{self.id} by {self.user_name}"

