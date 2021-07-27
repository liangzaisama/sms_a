"""自定义异常

MyExceptionError 根异常，根据初始化参数来进行错误响应
"""
from rest_framework import status

from security_platform import RET, ErrorType, ERROR_MAP, logger


class MyExceptionError(Exception):
    """自定义异常类

    抛出的自定义异常会被全局异常捕获，根据异常的error_response进行错误响应

    Attributes:
        errcode (str): 错误码，默认为 default_errcode
        errmsg (str): 错误描述，默认为根据code及errcode获取对于的错误描述
        status_code (int): HTTP状态码, 默认为 default_status_code
        code (str): 错误类型，默认为default
        detail (str): 错误描述
    """
    default_errcode = RET.PARAMERR
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, errcode=None, errmsg=None, status_code=None, headers=None,
                 code=ErrorType.DEFAULT, **kwargs):
        """初始化"""
        if errcode is None:
            errcode = self.default_errcode

        if errmsg is None:
            errmsg = self.get_error_map(errcode, code, **kwargs)

        if status_code is None:
            status_code = self.default_status_code

        self.errcode = errcode
        self.errmsg = errmsg
        self.status_code = status_code
        self.headers = headers

    def get_error_map(self, errcode, code, **kwargs):
        """获取错误描述

        Args:
            errcode (str): 错误码
            code (str): 错误类型
            kwargs (dict): 错误描述的格式化字符串

        Returns:
            msg (str): 错误描述

        Raises:
            AssertionError: 当获取不到错误描述映射时报错
        """
        try:
            msg = ERROR_MAP[errcode][code]
        except KeyError as exc:
            logger.warning('缺少错误描述映射:%s', exc)
            msg = ERROR_MAP[errcode]['default']

        return msg.format(**kwargs)

    def __str__(self):
        """返回错误描述"""
        return self.errmsg


class NotFoundError(MyExceptionError):
    """服务内部异常"""
    default_errcode = RET.ROUTEERR
    default_status_code = status.HTTP_404_NOT_FOUND


class IPNotAllowed(MyExceptionError):
    """请求ip地址不允许"""
    default_errcode = RET.IPNOTALLOWED
    default_status_code = status.HTTP_403_FORBIDDEN


class ServerError(MyExceptionError):
    """服务内部异常"""
    default_errcode = RET.SERVERERR
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class RequestVMSError(ServerError):
    """请求视频监控视频"""
    pass


class BadRequestError(MyExceptionError):
    """错误请求"""
    pass


class JwtAuthenticationError(MyExceptionError):
    """jwt验证失败"""
    default_errcode = RET.AUTHENTICAERR
    default_status_code = status.HTTP_401_UNAUTHORIZED


class ParamError(BadRequestError):
    """内部参数错误"""
    pass


class ExParamError(BadRequestError):
    """外部参数错误"""
    default_errcode = RET.EXPARAMERR


class ValidationError(BadRequestError):
    """序列化器校验异常"""
    pass


class PermissionsError(BadRequestError):
    """无权限操作"""
    default_errcode = RET.PERMISSIONERR
    default_status_code = status.HTTP_403_FORBIDDEN


class CustomerDisallowHostError(BadRequestError):
    """访问域名错误"""
    default_errcode = RET.DISAlOWHOSTERR
    default_status_code = status.HTTP_403_FORBIDDEN
