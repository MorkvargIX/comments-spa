from django.db.models import Count
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.comments.models import Comment, Attachment
from apps.comments.serializers import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentReadSerializer
)
from apps.comments.pagination import CommentPagination, ReplyPagination
from apps.comments.services import (
    generate_captcha_text,
    generate_captcha_image,
    store_captcha,
)


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
            qs = qs.prefetch_related('attachments')
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


class CaptchaView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        text = generate_captcha_text()
        captcha_id = store_captcha(text)
        image = generate_captcha_image(text)

        return Response(
            {
                'captcha_id': captcha_id,
                'image': image,  # base64
            },
            status=status.HTTP_200_OK,
        )


class AttachmentDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        try:
            attachment = Attachment.objects.get(pk=pk)
        except Attachment.DoesNotExist:
            raise Http404

        return FileResponse(
            attachment.file.open('rb'),
            as_attachment=False,
            filename=attachment.original_name,
        )
