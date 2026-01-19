from django.db import models


class AuditMixin(models.Model):
    """
    Base audit fields for models.
    Provides created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created at",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated at",
    )

    class Meta:
        abstract = True
