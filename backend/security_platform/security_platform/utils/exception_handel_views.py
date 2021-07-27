"""
自定义接口处理视图
my_exception_handler 全局异常捕获
"""
from collections import OrderedDict

from redis import RedisError
from rest_framework import status
from rest_framework import exceptions
from rest_framework.views import exception_handler
from django.http import JsonResponse
from django.core.exceptions import DisallowedHost
from django.db import DatabaseError, InterfaceError

from security_platform import logger, RET
from security_platform.utils.views import CustomGenericAPIView
from security_platform.utils.exceptions import (
    BadRequestError, ServerError, MyExceptionError, NotFoundError, CustomerDisallowHostError, PermissionsError
)

# 需要调整返回消息的rest异常
REST_FRAMEWORK_EXCEPTION_MAP = {
    exceptions.ParseError: RET.PARSEERR,
    exceptions.AuthenticationFailed: RET.AUTHENTICAERR,
    exceptions.NotAuthenticated: RET.AUTHENTICAERR,
    exceptions.PermissionDenied: RET.PERMISSIONERR,
    exceptions.NotFound: RET.ROUTEERR,
    # exceptions.MethodNotAllowed: METHODERR,
    # exceptions.NotAcceptable: NOTACCEPTABLEERR,
    exceptions.UnsupportedMediaType: RET.MEDIATYPEERR,
    # exceptions.Throttled: THROTTLEDERR
}


def get_my_exception_error_response(exc):
    """自定义异常处理"""
    response = CustomGenericAPIView.error_response(
        errmsg=exc.errmsg,
        errcode=exc.errcode,
        status_code=exc.status_code,
        headers=exc.headers
    )

    return response


# noinspection PyUnresolvedReferences, PyProtectedMember
def drf_error_handler(exc, context):
    """drf框架异常处理"""
    response = exception_handler(exc, context)
    errcode = REST_FRAMEWORK_EXCEPTION_MAP.get(type(exc))

    exc_kwargs = OrderedDict(
        errcode=errcode,
        status_code=response.status_code,
        headers=dict(response._headers.values())
    )

    if errcode is None:
        exc_kwargs['errcode'] = getattr(RET, exc.__class__.__name__.upper(), RET.BADREQUESTERR)
        exc_kwargs['errmsg'] = str(exc.detail)

    return system_error_handler(BadRequestError(**exc_kwargs), context)


def system_error_handler(exc, context):
    """系统内部异常处理 rest_framework视图

    处理异常包括，内部自定义抛出异常，mysql异常，redis异常，程序未知异常
    """
    if isinstance(exc, MyExceptionError):
        return get_my_exception_error_response(exc)

    if isinstance(exc, (DatabaseError, InterfaceError)):
        logger.error('[%s]：操作mysql数据库异常', context['view'], exc_info=True)
        exc = ServerError(errcode=RET.MYSQLERR, status_code=status.HTTP_507_INSUFFICIENT_STORAGE)

    elif isinstance(exc, (RedisError,)):
        logger.error('[%s]：操作redis数据库异常', context['view'], exc_info=True)
        exc = ServerError(errcode=RET.REDISERR, status_code=status.HTTP_507_INSUFFICIENT_STORAGE)
    else:
        logger.error('[%s] 未知错误', context['view'], exc_info=True)
        exc = ServerError(errcode=RET.SERVERERR)

    return system_error_handler(exc, context)


def my_exception_handler(exc, context):
    """全局异常处理

    分为rest框架异常，和异常内部异常

    Args:
        exc : 抛出的异常
        context : 上下文字典，包含了抛出异常的视图及请求等
    """
    if isinstance(exc, exceptions.APIException):
        return drf_error_handler(exc, context)

    return system_error_handler(exc, context)


def rest_resp_transform_json_resp(exc):
    response = get_my_exception_error_response(exc)
    return JsonResponse(data=response.data, status=response.status_code)


def bad_request(request, exception):
    """django400异常处理"""
    if isinstance(exception, DisallowedHost):
        # 访问域名异常
        return rest_resp_transform_json_resp(CustomerDisallowHostError())

    return rest_resp_transform_json_resp(BadRequestError())


def permission_denied(request, exception):
    """django403异常处理"""
    return rest_resp_transform_json_resp(PermissionsError())


def page_not_found(request, exception):
    """django404异常处理"""
    return rest_resp_transform_json_resp(NotFoundError())


def server_error(exception):
    """django500异常处理"""
    return rest_resp_transform_json_resp(ServerError())
