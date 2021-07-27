"""mixin工具类

包含自定义异常抛出工具类
自定义接口响应
序列化器批量操作工具类
"""
from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from security_platform.utils.exceptions import ParamError, ExParamError


def _get_response_success_data(data):
    """请求成功业务字段

    只有data的布尔值为True或者data为空列表的情况下存在

    Args:
        data: 响应数据

    Returns:
        success_data: 成功响应结果字典
    """
    success_data = OrderedDict(result='success')

    if data or data == []:
        success_data['data'] = data

    return success_data


def _get_response_error_data(errcode, errmsg):
    """请求失败业务字段

    Args:
        errcode: 错误码
        errmsg: 错误描述

    Returns:
        fail_data: 错误响应结果字典
    """
    return OrderedDict(result='error', error_code=errcode, error_message=errmsg)


class CustomErrorHandleMixin:
    """自定义异常抛出"""

    def param_error(self, *args, external=False, **kwargs):
        """参数校验异常抛出

        Args:
            external: 外部错误，默认内部错误
            **kwargs: 初始化参数

        Raises:
            param_exception_class: 抛出的异常
        """
        if external:
            raise ExParamError(*args, **kwargs)

        raise ParamError(*args, **kwargs)

    def validate_error(self, *args, **kwargs):
        """参数校验异常抛出, 比param_error名称更合适，后续将去掉param_error"""
        self.param_error(*args, **kwargs)


class CustomResponseMixin:
    """自定义响应工具类"""

    def add_operation_field(self, response):
        """增加业务字段"""
        response.data = _get_response_success_data(response.data)
        return response

    @classmethod
    def success_response(cls, data=None, status_code=HTTP_200_OK, headers=None):
        """返回成功响应

        Args:
            data : 响应数据字典或列表
            status_code : http状态码 默认200
            headers :  响应头 默认为None

        Returns:
            response (Response): HTTP响应结果
        """
        return Response(data=_get_response_success_data(data), status=status_code, headers=headers)

    @classmethod
    def error_response(cls, errcode, errmsg, status_code=HTTP_400_BAD_REQUEST, headers=None):
        """错误响应

        Args:
            errcode (str): 错误码
            errmsg (str): 错误描述
            status_code (int): http状态码 默认400
            headers (dict): http响应头 默认为None

        Returns:
            response (Response): HTTP响应结果
        """
        return Response(data=_get_response_error_data(errcode, errmsg), status=status_code, headers=headers)
