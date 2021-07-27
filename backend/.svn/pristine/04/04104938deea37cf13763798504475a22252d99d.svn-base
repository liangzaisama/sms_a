"""查询集过滤器

CustomDjangoFilterBackend：增加url参数的校验失败后抛出异常
"""
from django_filters.rest_framework import DjangoFilterBackend

from security_platform.utils.exceptions import ValidationError


class CustomDjangoFilterBackend(DjangoFilterBackend):
    """自定义后端过滤器"""

    def error_process(self, error_dict):
        """错误处理，抛出异常"""
        for key, error_list in error_dict.as_data().items():
            raise ValidationError(param_name=key)

    def filter_queryset(self, request, queryset, view):
        """过滤查询集"""
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            self.error_process(filterset.errors)

        return filterset.qs
