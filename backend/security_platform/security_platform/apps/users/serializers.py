"""
用户接口序列化器
"""
import re

from rest_framework import serializers
from django.db import transaction, connection
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password as django_validate_password

from devices.models import DeviceInfo
from users.models import Department, User, UserIPWhiteList, UserBacklog
from security_platform import RET, ErrorType
from security_platform.utils.commen import iterable_to_str_tuple
from security_platform.utils.exceptions import PermissionsError
from security_platform.utils.serializer import CustomModelSerializer
from security_platform.utils.pagination import StandardResultsSetPagination


class UserPasswordSerializer(CustomModelSerializer):
    """用户修改密码序列化器"""

    old_password = serializers.CharField(required=True, write_only=True, label='原始密码')
    password_confirm = serializers.CharField(required=True, write_only=True, label='密码确认')

    class Meta:
        """模型类配置"""
        model = User
        fields = ('old_password', 'password', 'password_confirm')
        extra_kwargs = {'password': {
            'required': True,
            'write_only': True,
            'min_length': 8,
            'max_length': 36,
        }}

    def validate_old_password(self, old_password):
        """校验原始密码是否正确

        Args:
            old_password: 用户原始密码

        Returns:
            old_password: 用户原始密码

        Raises:
            ParamError: 原始密码不正确时抛出异常
        """
        if not self.instance.check_password(old_password):
            self.validate_error(errcode=RET.PWDERR, code=ErrorType.INVALID_OLD_PWD)

        return old_password

    def validate_password(self, password):
        """对新密码格式进行校验

        MinimumLengthValidator：长度不低于8位
        NumericPasswordValidator：密码不能全包含为数字

        Args:
            password: 新密码

        Returns:
            password: 新密码

        Raises:
            ParamError: 新密码格式错误时抛出异常
        """
        try:
            django_validate_password(password)
        except ValidationError as exc:
            self.validate_error(errcode=RET.PWDERR, errmsg=exc.messages[0])

        return password

    def validate_password_confirm(self, password_confirmation):
        """确认密码和新密码输入是否一致

        Args:
            password_confirmation: 确认密码

        Returns:
            password_confirmation: 确认密码

        Raises:
            ParamError: 确认密码和新密码不一致时抛出异常
        """
        if password_confirmation != self.initial_data['password']:
            self.validate_error(errcode=RET.PWDERR, code=ErrorType.DIFFERENT_PWD)

        return password_confirmation

    def update(self, user, validated_data):
        """更新用户密码

        Args:
            user: 要更新的用户模型类对象
            validated_data: 更新字段字典

        Returns:
            user: 更新后的模型类对象
        """
        user.update_password(validated_data['password'])
        return user


class UserScenarioSerializer(CustomModelSerializer):
    """用户场景值序列化器"""

    class Meta:
        """模型类配置"""
        model = User
        fields = ('scenario', )
        extra_kwargs = {'scenario': {'required': True}}

    def update(self, instance, validated_data):
        """更新用户场景值"""
        instance.scenario = validated_data['scenario']
        instance.save(update_fields=['scenario'])

        return instance


class UserInfoUpdateSerializer(CustomModelSerializer):
    """用户更新序列化器"""

    level = serializers.ChoiceField(choices=User.UserLevel.values)

    class Meta:
        """模型类配置"""
        model = User
        fields = ('department_id', 'level', 'is_active')
        extra_kwargs = {
            'is_active': {
                'required': True
            },
            'department_id': {
                'required': True,
                'source': 'department',
                'queryset': Department.objects.all().only('id'),
                'allow_null': False,
            },
        }

    def validate_department_id(self, department):
        """校验部门权限

        超级管理新增/查看/修改无部门限制
        部门管理员新增/查看/修改时必须为自身部门
        部门权限不足时抛出异常
        """
        if not self.user.is_superuser and self.user.department != department:
            raise PermissionsError(code=ErrorType.DEPARTMENT)

        return department

    def validate_level(self, level):
        """级别权限校验

        超级管理员新增/查看/修改无级别限制
        部门管理员新增/查看/修改时只能自己同级别或以下的员工
        用户级别不足时抛出异常
        """
        if not self.user.is_superuser and level == User.UserLevel.ADMIN:
            raise PermissionsError(code=ErrorType.LEVEL)

        return level


class UserInfoSerializer(UserInfoUpdateSerializer):
    """用户新增/列表序列化器"""

    username = serializers.CharField(
        label='用户名',
        min_length=6,
        max_length=20,
        # validators=[AbstractUser.username_validator],
    )

    class Meta(UserInfoUpdateSerializer.Meta):
        """模型类配置"""
        fields = ('user_id', 'username', 'staff_name', 'department_id', 'level', 'is_active')
        extra_kwargs = UserInfoUpdateSerializer.Meta.extra_kwargs
        extra_kwargs['staff_name'] = {'required': True, 'allow_blank': False, 'min_length': 2, 'max_length': 15}
        extra_kwargs['user_id'] = {'source': 'id'}

    def validate_username(self, username):
        try:
            AbstractUser.username_validator(username)
        except ValidationError:
            self.validate_error(errcode=RET.UNAEMERR)

        if User.raw_objects.filter(username=username).exists():
            self.validate_error(errcode=RET.UNAEMERR, code=ErrorType.UNIQUE)

        return username

    def create(self, validated_data):
        """新增用户"""
        with transaction.atomic():
            user = super().create(validated_data)
            user.update_password(settings.API_SETTINGS.DEFAULT_USER_PASSWORD)

        return user


class UserCloneSerializer(UserInfoSerializer):
    """用户克隆序列化器"""

    class Meta(UserInfoSerializer.Meta):
        """模型类配置"""
        fields = ('username', 'staff_name')

    @property
    def close_user(self):
        return self.context['clone_user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_id'] = instance.id
        data['level'] = instance.level
        data['department_id'] = instance.department_id
        data['is_active'] = instance.is_active

        return data

    def validate(self, attrs):
        attrs['department'] = self.close_user.department
        attrs['is_leader'] = self.close_user.is_leader
        attrs['scenario'] = self.close_user.scenario
        attrs['is_active'] = self.close_user.is_active

        return attrs

    def create(self, validated_data):
        """新增用户"""
        with transaction.atomic():
            user = CustomModelSerializer.create(self, validated_data)
            user.update_password(settings.API_SETTINGS.DEFAULT_USER_PASSWORD)
            user.device_set.set(self.close_user.device_set.all())

        return user


class BatchDeleteUserSerializer(CustomModelSerializer):
    """
    用户批量删除
    """
    user_ids = serializers.ListField(
        write_only=True,
        allow_empty=False,
        label='用户id列表',
        child=serializers.IntegerField()
    )

    class Meta:
        """模型类配置"""
        model = User
        fields = ('user_ids', )

    def validate_batch_count(self, user_ids):
        """批量操作数量校验

        超过分页最大数量限制后会报错，校验失败会抛出异常

        Args:
            user_ids: 要注销的用户id列表

        Raises:
            ParamError: 校验失败时抛出异常信息

        """
        if len(user_ids) > StandardResultsSetPagination.max_page_size:
            self.validate_error(
                errcode=RET.BATCHCOUNTERROR,
                function='注销用户',
                max_count=StandardResultsSetPagination.max_page_size
            )

    @property
    def queryset(self):
        """获取视图类的查询集"""
        view = self.context['view']
        return view.filter_queryset(view.get_queryset())

    def validate_user_ids(self, user_ids):
        """注销用户id校验

        包含批量最大数量校验、模型类对象是否存在的校验
        校验失败抛出参数异常
        """
        self.validate_batch_count(user_ids)

        users = User.objects.filter(id__in=user_ids).only('username')
        if len(users) != len(user_ids):
            self.validate_error(errmsg='存在错误或无权限的用户id')

        return users


class BatchDeleteUserIpSerializer(CustomModelSerializer):
    """
    用户ip批量删除
    """
    user_ip_ids = serializers.ListField(write_only=True, allow_empty=False, label='用户IP',
                                        child=serializers.IntegerField())

    class Meta:
        """模型类配置"""
        model = UserIPWhiteList
        fields = ('user_ip_ids', )

    def validate_user_ip_ids(self, user_ip_ids):
        """注销用户id校验"""
        if UserIPWhiteList.objects.filter(id__in=user_ip_ids).count() != len(user_ip_ids):
            self.validate_error(errmsg='存在错误或重复的ip_id')

        return user_ip_ids


class DepartmentSerializer(CustomModelSerializer):
    """部门列表序列化器"""

    class Meta:
        model = Department
        fields = ('department_id', 'department_name')
        extra_kwargs = {
            'department_id': {'source': 'id'},
        }


class PagePermissionSerializer(CustomModelSerializer):
    """部门页面权限序列化器"""

    class Meta:
        model = Department
        fields = ('page_permissions', )
        extra_kwargs = {'page_permissions': {
            'required': True,
            'allow_blank': False
        }}


class DepartmentDevicePermSerializer(CustomModelSerializer):
    """部门设备权限序列化器

    Class Attributes:
        device_ids: 修改部门权限时，传递的新的设备权限列表，用于反序列化字段校验
    """

    device_ids = serializers.ListField(
        write_only=True,
        label='设备ID列表',
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    action = serializers.ChoiceField(choices=[0, 1], write_only=True)

    class Meta:
        model = Department
        fields = ('device_ids', 'action')

    def validate_device_ids(self, device_ids):
        """校验设备id列表"""
        device_count = DeviceInfo.objects.filter(id__in=device_ids).count()

        if device_count != len(device_ids):
            self.validate_error(param_name='device_ids')

        return device_ids

    def get_execute_sql_list(self, devices, instance):
        """删除部门关联数据的sql

        删除部门下用户的关联设备
        删除部门下用户关联的设备组及设备标签设备

        Args:
            devices: 要删除权限的设备id列表
            instance: 部门对象

        Returns:
            sql_list: 执行的sql列表
        """
        devices = iterable_to_str_tuple(devices)
        users = iterable_to_str_tuple(instance.user_set.all().values_list('id', flat=True))

        return [
            f'delete from tb_device_info_users where deviceinfo_id in {devices} and user_id in {users};',

            f'delete from tb_device_group_devices where devicegroup_id in (select id from tb_device_group where '
            f'user_id in {users}) and deviceinfo_id in {devices};',

            f'delete from tb_device_label_devices where devicelabel_id in (select id from tb_device_label where '
            f'user_id in {users}) and deviceinfo_id in {devices};',
        ]

    def delete_related_devices(self, devices, instance):
        """执行删除关联数据的sql"""
        with connection.cursor() as cursor:
            for sql in self.get_execute_sql_list(devices, instance):
                cursor.execute(sql)

    # noinspection PyUnresolvedReferences,PyTypeChecker
    def update(self, instance, validated_data):
        """更新设备权限

        删除的情况下需要删除关联的数据

        Args:
            instance: 部门或用户对象
            validated_data: 参数数据字典

        Returns:
            instance: 部门或用户对象
        """
        devices = validated_data['device_ids']

        with transaction.atomic():
            if validated_data['action']:
                # 新增
                instance.device_set.add(*devices)
            else:
                # 删除
                instance.device_set.remove(*devices)
                self.delete_related_devices(devices, instance)

        return instance


class UserDevicePermSerializer(DepartmentDevicePermSerializer):
    """用户设备权限序列化器"""

    class Meta(DepartmentDevicePermSerializer.Meta):
        model = User

    def validate_device_ids(self, device_ids):
        """校验设备id列表"""

        # 要赋给用户的设备，必须隶属于该用户部门下的设备
        device_count = self.instance.department.device_set.filter(id__in=device_ids).count()

        if device_count != len(device_ids):
            # 存在未查询到的设备
            self.validate_error(errmsg='设备不存在或设备不属于用户部门下设备')

        return device_ids

    def get_execute_sql_list(self, devices, instance):
        """删除用户关联数据的sql

        需要删除用户关联的设备组及设备标签的设备

        Args:
            devices: 要删除权限的设备id列表
            instance: 用户对象

        Returns:
            sql_list: 执行的sql列表
        """
        devices = iterable_to_str_tuple(devices)

        return [
            f'delete from tb_device_group_devices where devicegroup_id in (select id from tb_device_group where '
            f'user_id = {instance.id}) and deviceinfo_id in {devices};',

            f'delete from tb_device_label_devices where devicelabel_id in (select id from tb_device_label where '
            f'user_id = {instance.id}) and deviceinfo_id in {devices};',
        ]


class UserIpSerializer(CustomModelSerializer):

    class Meta:
        model = UserIPWhiteList
        fields = ('ip_address', 'ip_id')
        extra_kwargs = {
            'ip_id': {
                'source': 'id',
                'read_only': True
            }
        }

    def validate_error(self, code):
        super(UserIpSerializer, self).validate_error(errcode=RET.EXPARAMERR, code=code, param_name='IP地址')

    def create_ip_validate(self, ip_address):
        user = self.context['user']

        # 校验是否存在重复ip地址
        if UserIPWhiteList.objects.filter(user=user, ip_address=ip_address).exists():
            self.validate_error(code=ErrorType.UNIQUE)

        # 校验最大数量
        if user.useripwhitelist_set.all().count() >= UserIPWhiteList.SINGLE_USER_MAX_COUNT:
            self.validate_error(code=ErrorType.MAX_COUNT)

    def update_ip_validate(self, ip_address):
        user = self.instance.user

        # 校验是否存在重复ip地址
        if UserIPWhiteList.objects.exclude(id=self.instance.id).filter(user=user, ip_address=ip_address).exists():
            self.validate_error(code=ErrorType.UNIQUE)

    def validate_ip_address(self, ip_address):
        """ip地址校验逻辑

        0.0.0.0~255.255.255.255
        最后一位为0表示该网段都可以访问
        """
        # 校验格式
        if not re.search(r'^(([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])$',
                         ip_address):
            self.validate_error(code=ErrorType.INVALID)

        if self.instance:
            # 修改
            self.update_ip_validate(ip_address)
        else:
            self.create_ip_validate(ip_address)

        return ip_address

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        return super(UserIpSerializer, self).create(validated_data)


class UserBacklogSerializer(CustomModelSerializer):

    class Meta:
        model = UserBacklog
        fields = ('object_id', 'description', 'backlog_type')
