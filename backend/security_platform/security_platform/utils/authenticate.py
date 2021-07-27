"""接口校验类

DefineJSONWebTokenAuthentication: jwt token校验
"""
import jwt
from django_redis import get_redis_connection
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, jwt_decode_handler

from security_platform import ErrorType
from security_platform.utils.exceptions import JwtAuthenticationError


class DefineJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """
    自定义token校验
    """
    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            raise JwtAuthenticationError(code=ErrorType.REQUIRED)

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            raise JwtAuthenticationError(code=ErrorType.EXPIRE)
        except jwt.DecodeError:
            raise JwtAuthenticationError()
        except jwt.InvalidTokenError:
            raise JwtAuthenticationError()

        user = self.authenticate_credentials(payload)
        if user:
            redis_conn = get_redis_connection(alias='session')
            if jwt_value != redis_conn.get(user.id):
                raise JwtAuthenticationError()

        return user, jwt_value
