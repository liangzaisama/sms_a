"""
用户模块api视图类
"""
from datetime import datetime
from collections import OrderedDict

from django.conf import settings
from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework_jwt.views import ObtainJSONWebToken

from users import serializers
from users.utils import aes_decrypt
from users.models import User, Department, UserIPWhiteList, UserBacklog
from users.filter import DevicePermFilter, UserPermFilter, UserFilter
from devices.serializers import DeviceBasicSerializer
from security_platform import RET, ErrorType
from security_platform.utils.filters import CustomDjangoFilterBackend
from security_platform.utils.permisssions import SystemManagerPermission, DepartmentLeaderPermission
from security_platform.utils.views import (
    CustomGenericAPIView, RetrieveUpdateCustomAPIView, ListCustomAPIView,
    CreateListCustomAPIView, UpdateCustomAPIView, UpdateListCustomAPIView,
)


class UserAuthorizeView(ObtainJSONWebToken, CustomGenericAPIView):
    """登陆接口

    用户密码需要加密：使用aes算法加解密
    同一用户无法使用多个token进行登录: 使用redis存储已登录用户的token，用户重复登录会替换之前已有的token
    """
    SECRET_SUB_LENGTH = 16

    def write_redis_for_token(self, user, token):
        """使用redis保存用户token

        redis保存格式为字符串，用户id为字符串的key，token为value

        Args:
            user: 用户对象
            token: 要保存的token
        """
        redis_conn = get_redis_connection(alias='session')
        redis_conn.set(user.id, token, ex=settings.EXPIRE_DAYS * 86400)

    # noinspection PyBroadException
    def perform_password_decrypt(self, password):
        """执行密码解密"""
        try:
            decrypt_password = aes_decrypt(settings.SECRET_KEY[:self.SECRET_SUB_LENGTH], password)
        except Exception:
            return self.param_error(code=ErrorType.DECRYPT, errcode=RET.LOGINERR)

        return decrypt_password

    # noinspection PyUnboundLocalVariable
    def validate_user(self, request):
        """校验用户名及密码"""
        username = request.data.get('username')
        password = request.data.get('password')
        disable_encrypt = request.data.get('disable_encrypt')

        if not disable_encrypt:
            password = self.perform_password_decrypt(password)

        try:
            user = User.objects.raw('select * from users_user where binary username="{0}" and '
                                    'is_deleted=0'.format(username))[0]
        except Exception:
            self.param_error(errcode=RET.LOGINERR)

        if not user.check_password(password):
            self.param_error(errcode=RET.LOGINERR)

        if not user.is_active:
            self.param_error(errcode=RET.ACTIVEERR)

        request.user = user
        self.check_auth_ip(request)

        return user

    def generate_auth_token(self, user):
        """生成jwt token"""
        token = user.generate_token
        self.write_redis_for_token(user, token)

        return token

    def create_resp_login_data(self, token, user):
        """构造登录响应数据"""
        data = OrderedDict()
        data['token'] = token
        data['scenario'] = user.scenario
        data['user_id'] = user.id
        data['username'] = user.username
        data['staff_name'] = user.staff_name
        data['department_id'] = user.department_id
        data['level'] = user.level

        if data['level'] != User.UserLevel.ADMIN:
            data['page_permissions'] = user.department.page_permissions

        return data

    def post(self, request, *args, **kwargs):
        """处理登录post请求"""
        user = self.validate_user(request)
        token = self.generate_auth_token(user)

        return self.success_response(data=self.create_resp_login_data(token, user))


class DepartmentPagePermissionView(SystemManagerPermission, RetrieveUpdateCustomAPIView):
    """部门页面权限视图

    接口权限控制：超级管理员
    使用page_permissions字段来控制部门页面权限，后端不做限制，由前端控制页面权限

    GET: 获取部门页面权限
    PUT: 修改部门页面权限
    """
    serializer_class = serializers.PagePermissionSerializer
    queryset = Department.objects.all().only('page_permissions')


class DepartmentDevicePermissionView(SystemManagerPermission, UpdateListCustomAPIView):
    """部门设备数据权限视图

    接口权限控制：超级管理员
    GET: 获取部门设备权限
    PUT: 修改部门设备权限
    """
    serializer_class = serializers.DepartmentDevicePermSerializer
    queryset = Department.objects.all().only('id')
    filter_backends = (CustomDjangoFilterBackend, )
    filter_class = DevicePermFilter

    def is_get_method(self):
        """判断是否是get请求"""
        return self.request.method == 'GET'

    def get_serializer_class(self):
        """获取序列化器

        get请求时返回设备序列化器
        """
        if self.is_get_method():
            return DeviceBasicSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        """获取查询集

        get请求时返回对象关联设备权限的模型类查询集
        """
        if self.is_get_method():
            return self.get_instance_devices(self.get_object())

        return super().get_queryset()

    # noinspection PyTypeChecker,PyUnboundLocalVariable
    def get_object(self):
        """获取模型类对象

        这里是获取用户或部门对象，并对当前登录用户对操作对象的权限进行校验
        部门无权限校验
        用户存在相关权限校验，用户等级，用户部门等

        Returns:
            obj: 模型类对象

        Raises:
            ParamError: 获取对象失败时抛出异常
            PermissionsError: 用户操作用户权限不足时会抛出异常
        """
        try:
            obj = self.queryset.get(pk=self.kwargs['pk'])
        except self.queryset.model.DoesNotExist:
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name=self.model_name)

        self.check_object_permissions(self.request, obj)

        return obj

    @property
    def device_fields(self):
        """设备模型类获取的字段

        防止数据库查询不需要的字段，方便子类进行替换修改

        Returns:
            device_fields: 要查询的字段
        """
        return ['id', 'device_name', 'device_type', 'device_code']

    def validate_exclude_user_id(self, exclude_user_id):
        """校验用户id"""
        if not User.objects.filter(id=exclude_user_id).exists():
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name='用户')

        return exclude_user_id

    # noinspection PyUnresolvedReferences
    def get_instance_devices(self, instance):
        """获取部门拥有的设备权限"""
        queryset = instance.device_set.all()

        exclude_user_id = self.request.query_params.get('exclude_user_id')
        if exclude_user_id is not None:
            self.validate_exclude_user_id(exclude_user_id)
            queryset = queryset.exclude(users=exclude_user_id)

        return queryset.only(*self.device_fields).order_by('-id')


# noinspection PyUnresolvedReferences
class UserDevicePermissionView(DepartmentLeaderPermission, DepartmentDevicePermissionView):
    """用户设备数据权限视图

    接口权限控制：超级管理员，部门管理员

    GET: 获取用户设备权限
    PUT: 修改用户设备权限

    operated_user_levels: 限制用户等级，只有普通员工有权限被操作
    """
    operated_user_levels = (User.UserLevel.STAFF, )
    serializer_class = serializers.UserDevicePermSerializer
    queryset = User.objects.all().only('id')

    def get_instance_devices(self, instance):
        """获取用户拥有的设备权限"""
        return instance.device_set.all().only(*self.device_fields).order_by('-id')


class DepartmentView(ListCustomAPIView):
    """获取部门列表

    GET: 获取部门列表
    """
    pagination_class = None
    serializer_class = serializers.DepartmentSerializer
    queryset = Department.objects.all().only('id', 'department_name').order_by('id')


class UserScenarioView(UpdateCustomAPIView):
    """用户场景值

    PUT: 修改场景值
    """
    serializer_class = serializers.UserScenarioSerializer

    def get_object(self):
        """获取用户对象"""
        return self.request.user


class UserPasswordView(UpdateCustomAPIView):
    """用户密码

    PUT: 修改密码
    """
    serializer_class = serializers.UserPasswordSerializer

    def get_object(self):
        """获取用户对象"""
        return self.request.user


class UserPasswordDefaultView(DepartmentLeaderPermission, CustomGenericAPIView):
    """重置用户密码

    接口权限控制：超级管理员，部门管理员

    PUT: 重置用户密码
    """
    queryset = User.objects.all().only('id')

    def put(self, request, *args, **kwargs):
        """处理请求"""
        user = self.get_object()
        user.update_password(settings.API_SETTINGS.DEFAULT_USER_PASSWORD)

        return self.success_response()


class UserInfoUpdateView(DepartmentLeaderPermission, UpdateCustomAPIView):
    """用户信息更新

    接口权限控制：超级管理员，部门管理员
    PUT: 用户信息更新
    """
    serializer_class = serializers.UserInfoUpdateSerializer
    queryset = User.objects.all().only('id')


# noinspection PyUnresolvedReferences
class UserInfoView(DepartmentLeaderPermission, CreateListCustomAPIView):
    """用户信息

    POST: 新增用户(需要超级管理员/部门管理员权限)
    GET: 获取用户列表
    """
    validate_data = None
    ordering = ['-id']
    ordering_fields = ['id']
    filter_class = UserFilter
    filter_backends = (CustomDjangoFilterBackend, OrderingFilter)
    serializer_class = serializers.UserInfoSerializer
    queryset = User.objects.all().only(
        'username', 'staff_name', 'is_active', 'department_id', 'is_leader', 'is_superuser'
    )

    def is_add_default_department(self, request):
        """判断是否增加默认部门"""
        return not request.user.is_superuser and 'department_id' not in request.query_params

    def get_permissions(self):
        if self.request.method == 'GET':
            # 获取用户列表时跳过权限校验
            return []

        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """用户列表

        超级管理员：访问无限制
        部门管理员：查询用户限制为自己的部门，查询级别限制自身等级及以下的用户

        部门管理员过滤条件未传递部门id时，默认为自身部门id，传递别的部门时会返回权限不足
        部门管理员过滤条件未传递等级时，默认排除超级管理员用户
        """
        if self.is_add_default_department(request):
            query_params = request.query_params.copy()
            query_params['department_id'] = request.user.department_id
            # noinspection PyProtectedMember
            request._request.GET = query_params

        return super().get(request, *args, **kwargs)


class BatchUserView(DepartmentLeaderPermission, CustomGenericAPIView):
    """用户批量操作视图

    接口权限控制：超级管理员，部门管理员
    对用户查询集进行权限过滤，保证当前登录用户没有操作权限的用户不在查询集中

    DELETE: 批量用户注销
    """
    queryset = User.objects.all()
    filter_backends = (UserPermFilter, )
    serializer_class = serializers.BatchDeleteUserSerializer

    def perform_delete(self, serializer):
        """数据库逻辑删除用户"""
        users = serializer.validated_data['user_ids']
        with transaction.atomic():
            for user in users:
                user.is_deleted = True
                user.username = f'{user.username}(该用户已于{datetime.now()}注销)'
                user.save()

    def delete(self, request):
        """批量注销用户请求处理"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_delete(serializer)

        return self.success_response(status_code=status.HTTP_204_NO_CONTENT)


class UserIpCreateListView(DepartmentLeaderPermission, CreateListCustomAPIView):
    """用户ip列表/新增"""

    queryset = User.objects.all()
    serializer_class = serializers.UserIpSerializer

    def get_serializer_context(self):
        """序列化器上下文增加用户"""
        context = super().get_serializer_context()
        context['user'] = self.get_object()
        return context

    def list(self, request, *args,  **kwargs):
        """用户ip列表"""
        queryset = UserIPWhiteList.objects.filter(user=self.get_object()).order_by('-id')
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data)


class UserIpUpdateView(DepartmentLeaderPermission, UpdateCustomAPIView):
    """用户授权ip更新"""

    queryset = UserIPWhiteList.objects.all()
    serializer_class = serializers.UserIpSerializer


class BatchUserIpView(DepartmentLeaderPermission, CustomGenericAPIView):
    """用户ip批量操作视图

    DELETE: 批量用户ip删除
    """
    queryset = UserIPWhiteList.objects.all()
    serializer_class = serializers.BatchDeleteUserIpSerializer

    def perform_delete(self, serializer):
        """数据库逻辑删除用户"""
        self.queryset.model.objects.filter(id__in=serializer.validated_data['user_ip_ids']).delete()

    def delete(self, request):
        """用户删除"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_delete(serializer)

        return self.success_response(status_code=status.HTTP_204_NO_CONTENT)


class UserCloneView(DepartmentLeaderPermission, CreateListCustomAPIView):
    """用户克隆接口"""

    queryset = User.objects.all()
    serializer_class = serializers.UserCloneSerializer

    def get_serializer_context(self):
        """获取序列化器上下文，增加被克隆用户对象"""
        context = super().get_serializer_context()
        context['clone_user'] = self.get_object()
        return context


class UserBacklogView(CreateListCustomAPIView):

    serializer_class = serializers.UserBacklogSerializer
    queryset = UserBacklog.objects.all().order_by('-id')

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
