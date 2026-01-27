from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.comments.views import CommentViewSet, CaptchaView, AttachmentDetailView

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("captcha/", CaptchaView.as_view(), name="captcha"),
    # urls.py
    path(
        "attachments/<int:pk>/",
        AttachmentDetailView.as_view(),
        name='attachment-detail'
    ),
    path("", include(router.urls)),
]
