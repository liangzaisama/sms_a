"""相关自定义权限

接口功能权限： IsLeaderUser: 部门管理员，超级管理员可访问，并对接口操作的用户对象进行权限校验
设备对象权限：对部门及设备拥有的设备权限进行校验
"""
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated

from users.models import User
from devices.models import DeviceInfo
from security_platform import ErrorType
from security_platform.utils.exceptions import PermissionsError


class IsLeaderUser(BasePermission):
    """部门领导、超级管理可访问权限控制"""

    def has_permission(self, request, view):
        """判断是否拥有权限"""
        return request.user and (request.user.is_leader or request.user.is_superuser)

    def _has_object_permission(self, request, view, obj):
        """用户权限校验"""
        operated_user_levels = getattr(view, 'operated_user_levels', None)

        if any([
            # 自己不可以操作自己
            # request.user == obj,

            # 部门管理员操作超级管理员或非本部门下的用户
            (not request.user.is_superuser) and (obj.is_superuser or not request.user.is_same_department(obj)),

            # 用户等级不支持被操作
            operated_user_levels is not None and obj.level not in operated_user_levels
        ]):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """用户权限校验"""
        if not isinstance(obj, User):
            return True

        if not self._has_object_permission(request, view, obj):
            raise PermissionsError(code=ErrorType.USER)

        return True


class DeviceObjectPermissions(BasePermission):
    """
    设备权限功能校验
    """

    def has_object_permission(self, request, view, obj):
        """
        校验设备权限，返回True代表有权限，返回False代表没有权限
        """
        if not isinstance(obj, DeviceInfo) or not obj.is_belong_user(request.user):
            raise PermissionsError(code=ErrorType.DEVICE)

        return True


class DeviceObjectPermission:
    """设备数据权限类

    继承该类的视图会对设备权限进行校验
    使用功能：设备增删改查相关接口

    Examples：
        class DeviceAPIView(DeviceObjectPermission, CustomGenericAPIView):
            pass
    """

    permission_classes = (IsAuthenticated, DeviceObjectPermissions)


class SystemManagerPermission:
    """系统管理权限类

    继承该类视图只有超级管理员有权限操作，非超管用户一律禁止操作
    功能包括：用户增删改查、页面权限数据权限配置等

    Examples：
        class SystemAPIView(SystemManagerPermissionMixin, CustomGenericAPIView):
            pass
    """

    permission_classes = (IsAdminUser, )


class DepartmentLeaderPermission:
    """部门领导权限管理类"""

    operated_user_levels = None
    permission_classes = (IsLeaderUser, )
