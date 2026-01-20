from rest_framework.pagination import PageNumberPagination


class CommentPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = None
    max_page_size = 25


class ReplyPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
