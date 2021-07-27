"""自定义视图集

在原rest_framework 视图集基础上增加了自定义异常处理及批量操作接口分发
"""
from rest_framework import mixins
from rest_framework.viewsets import ViewSetMixin

from security_platform.utils.views import CustomGenericAPIView


class CustomGenericViewSet(ViewSetMixin, CustomGenericAPIView):
    pass


class CustomModelViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         CustomGenericViewSet):

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
