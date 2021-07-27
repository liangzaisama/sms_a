from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """分页配置"""

    # 默认每页数量
    page_size = 50

    # 指明前端可以通过per_page参数 说明每页数量
    page_size_query_param = 'per_page'

    # 每页最大数
    max_page_size = 200

    def get_paginated_response(self, data):
        # if not data:
        #     # 无数据
        #     return Response({'objects': data})

        # noinspection PyUnresolvedReferences
        return Response({
            'next': self.get_next_link(),  # 下一页的链接
            'previous': self.get_previous_link(),  # 上一页的链接
            'total_page': self.page.paginator.num_pages,  # 总页数
            'total_count': self.page.paginator.count,  # 总个数
            'objects': data  # 数据列表
        })
