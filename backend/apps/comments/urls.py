from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.comments.views import CommentViewSet, CaptchaView

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("captcha/", CaptchaView.as_view(), name="captcha"),
    path("", include(router.urls)),
]
