from rest_framework.pagination import (
    PageNumberPagination,
    # LimitOffsetPagination
)


class ResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class FollowResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'recipes_limit'
