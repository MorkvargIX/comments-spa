from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from apps.comments.models import Comment
from apps.comments.serializers import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentReadSerializer
)
from apps.comments.pagination import CommentPagination, ReplyPagination


class CommentViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    pagination_class = CommentPagination
    filter_backends = [OrderingFilter]

    ordering_fields = (
        'user_name',
        'email',
        'created_at',
    )
    ordering = ('-created_at',)

    def get_queryset(self):
        qs = (
            Comment.objects.filter(parent__isnull=True)
            .annotate(replies_count=Count('replies'), attachments_count=Count('attachments'))
        )
        if self.action == 'retrieve':
            qs.prefetch_related('attachments')
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        if self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentReadSerializer

    @action(detail=True, methods=['get'], pagination_class=ReplyPagination)
    def replies(self, request, pk=None):
        queryset = (
            Comment.objects.filter(parent_id=pk).
            annotate(replies_count=Count('replies'), attachments_count=Count('attachments')).
            order_by('created_at')
        )

        page = self.paginate_queryset(queryset)
        serializer = CommentReadSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)