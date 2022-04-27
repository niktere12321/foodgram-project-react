from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'limit'
