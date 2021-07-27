"""
自定义接口处理视图
CustomGenericAPIView 自定义视图，增加了内部异常抛出及接口响应格式
my_exception_handler 全局异常捕获
"""
from django.conf import settings
from django.http import Http404
from rest_framework import mixins
from rest_framework.generics import GenericAPIView

from security_platform import ErrorType
from security_platform.utils.exceptions import IPNotAllowed
from security_platform.utils.mixins import CustomErrorHandleMixin, CustomResponseMixin


# noinspection PyProtectedMember
class CustomGenericAPIView(GenericAPIView, CustomErrorHandleMixin, CustomResponseMixin):
    """通用视图

    包含自定义异常抛出
    包含请求成功，请求失败通用响应数据函数
    包含批量请求分发

    默认包含1层权限校验
    IsAuthenticated：用户是否认证校验
    """
    ip_check_classes = settings.API_SETTINGS.DEFAULT_IP_CHECK_CLASSES

    def is_batch_method(self, request):
        """判断是否是批量方法"""
        return request.path.endswith('batch') and request.method == 'POST'

    def validate_batch_method(self, request):
        """校验批量请求方式参数"""
        batch_method = request.data.get('method')

        if batch_method is None:
            self.param_error(code=ErrorType.REQUIRED, param_name='method')

        return batch_method

    def validate_batch_data(self, request):
        """校验批量数据参数"""
        batch_data = request.data.get('batch_data')

        if batch_data is None:
            self.param_error(code=ErrorType.REQUIRED, param_name='batch_data')

        if not isinstance(batch_data, dict):
            self.param_error(code=ErrorType.INVALID, param_name='batch_data')

        return batch_data

    def check_batch(self, request):
        """检查是否是批量方法"""
        if self.is_batch_method(request):
            batch_method = self.validate_batch_method(request)
            batch_data = self.validate_batch_data(request)
            request.method = batch_method
            request._full_data = batch_data

    def get_ip_check(self):
        return [ip_check() for ip_check in self.ip_check_classes]

    def check_auth_ip(self, request):
        for ip_check in self.get_ip_check():
            if not ip_check.validate(request, self):
                raise IPNotAllowed()

    def initial(self, request, *args, **kwargs):
        """在原有基础上增加批量校验"""
        super().initial(request, *args, **kwargs)
        self.check_auth_ip(request)
        self.check_batch(request)

    @property
    def model_name(self):
        """获取模型类名称"""
        return self.queryset.model._meta.verbose_name

    def get_object(self):
        """重写原有函数，增加抛出异常捕获"""

        try:
            return super().get_object()
        except Http404:
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name=self.model_name)


class UpdateCustomAPIView(mixins.UpdateModelMixin,
                          CustomGenericAPIView):

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ListCustomAPIView(mixins.ListModelMixin,
                        CustomGenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CreateCustomAPIView(mixins.CreateModelMixin,
                          CustomGenericAPIView):

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateCustomAPIView(mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  CustomGenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CreateListCustomAPIView(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              CustomGenericAPIView):

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UpdateListCustomAPIView(mixins.ListModelMixin,
                              mixins.UpdateModelMixin,
                              CustomGenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class NoPaginationListCustomAPIView(ListCustomAPIView):
    """无分页列表数据"""

    pagination_class = None
