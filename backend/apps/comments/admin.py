from django.contrib import admin
from .models import Comment, Attachment


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 0
    readonly_fields = ('file', 'type', 'original_name', 'created_at')
    can_delete = False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'email', 'created_at')
    search_fields = ('user_name', 'email', 'body')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    inlines = (AttachmentInline,)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'type', 'original_name', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('original_name',)
    raw_id_fields = ('comment',)
    ordering = ('-created_at',)
