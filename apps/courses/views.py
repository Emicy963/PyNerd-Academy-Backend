from rest_framework import pagination

class StandardResultSetPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 50
