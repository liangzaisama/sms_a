"""
用户模型类

数据库中
字符串字段允许为null和空
非字符串字段允许为null, 不允许为空

django中
所有字段可以设置null值和空值
字符串字段默认设置为 blank = true, 数据库中默认设置为空值
其他字段默认设置为 null = true, blank = true(表单校验时使用，写不写没影响只影响django的表单校验),
数据库中默认设置为null值, 强行传入空会报错

序列化器校验
字符串字段，传空跳过校验
非字符串字段，传null跳过检验，传空不跳过校验会报错

"""
from collections import OrderedDict

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from rest_framework_jwt.settings import api_settings

from security_platform import TextChoices
from security_platform.utils.models import BaseModel, FilterIsDeletedManager


class Department(models.Model):
    """部门表

    与用户是一对多关系
    与设备是多对多关系
    部门功能权限是页面权限，由前端进行控制，后端不做任何处理
    """

    department_name = models.CharField('部门名称', max_length=20, unique=True)
    page_permissions = models.TextField('页面权限', blank=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        db_table = 'tb_department'

    @property
    def device_ids(self):
        """获取部分拥有设备权限id列表"""
        return self.device_set.all().values_list('id', flat=True)

    def __str__(self):
        return self.department_name


class FilterIsDeletedUserManager(FilterIsDeletedManager, UserManager):
    """自定义Manager

    让原生object可以排除掉逻辑删除的用户
    """
    pass


# noinspection PyUnresolvedReferences
class UserMixin:

    @property
    def device_ids(self):
        """获取部分拥有设备权限id列表"""
        return self.device_set.all().values_list('id', flat=True)

    @property
    def generate_token(self):
        """生成jwt token"""
        return api_settings.JWT_ENCODE_HANDLER(api_settings.JWT_PAYLOAD_HANDLER(self))

    def update_password(self, raw_password):
        """更新密码"""
        self.set_password(raw_password)
        self.save(update_fields=["password"])

    @classmethod
    def get_field_value_by_level(cls, level):
        """根据等级获取对应的模型类字段

        Args:
            level: 等级

        Returns:
            level_relation_filed: 等级关联的对应字段字典
        """
        level_relation_filed = OrderedDict()

        if level == cls.UserLevel.ADMIN:
            level_relation_filed['is_leader'] = False
            level_relation_filed['is_staff'] = True
            level_relation_filed['is_superuser'] = True
        elif level == cls.UserLevel.LEADER:
            level_relation_filed['is_leader'] = True
            level_relation_filed['is_staff'] = False
            level_relation_filed['is_superuser'] = False
        elif level == cls.UserLevel.STAFF:
            level_relation_filed['is_leader'] = False
            level_relation_filed['is_staff'] = False
            level_relation_filed['is_superuser'] = False

        return level_relation_filed

    @property
    def level(self):
        """获取当前用户等级"""
        if self.is_superuser:
            level = self.UserLevel.ADMIN
        elif self.is_leader:
            level = self.UserLevel.LEADER
        else:
            level = self.UserLevel.STAFF

        return level

    @level.setter
    def level(self, value):
        """设置用户等级

        Args:
           value: 用户等级
        """
        for filed, filed_value in self.get_field_value_by_level(value).items():
            setattr(self, filed, filed_value)

    def is_same_department(self, user):
        """判断是否为相同部门"""
        return self.department_id == user.department_id


class User(AbstractUser, UserMixin):
    """用户表"""

    class UserLevel(TextChoices):
        """用户等级

        用于在接口层面实现用户等级，数据库层面体现在用户多个字段上
        超级管理员 = is_superuser True
        部门领导 = is_leader True
        部门员工 = is_leader False  is_superuser False
        """
        ADMIN = 'admin', '超级管理员'
        LEADER = 'leader', '部门领导'
        STAFF = 'staff', '部门员工'

    department = models.ForeignKey(Department, verbose_name='部门', on_delete=models.PROTECT, null=True, blank=True)
    is_leader = models.BooleanField('部门领导', default=False)
    mobile = models.CharField('电话', max_length=15, blank=True)
    scenario = models.TextField('自定义场景值(前端传递)', blank=True)
    staff_name = models.CharField('员工姓名', max_length=10, blank=True, db_index=True)
    is_deleted = models.BooleanField('逻辑删除', default=False, db_index=True)

    objects = FilterIsDeletedUserManager()
    raw_objects = UserManager()

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['is_leader', 'is_staff', 'is_superuser']),
        ]

    def __str__(self):
        return self.username


class UserIPWhiteList(BaseModel):
    """用户IP白名单"""

    SINGLE_USER_MAX_COUNT = 10
    user = models.ForeignKey(User, verbose_name="用户", null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.CharField('授权ip地址', max_length=15)

    class Meta:
        verbose_name = '用户ip白名单'
        db_table = 'tb_user_ip_white_list'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'ip_address']

    def __str__(self):
        return f'{self.user}-{self.ip_address}'


class UserDiary(BaseModel):
    """用户日志"""

    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='diary')
    job_content = models.CharField('工作内容', max_length=100)
    job_time = models.DateTimeField('时间')
    is_handover = models.BooleanField('是否交接', default=False)
    handover_user = models.ForeignKey(User, verbose_name='交接用户', on_delete=models.CASCADE)
    handover_content = models.CharField('交接内容', max_length=100)
    is_confirm = models.BooleanField('是否确认', default=False)

    class Meta:
        verbose_name = '用户日志'
        verbose_name_plural = verbose_name
        db_table = 'tb_user_diary'

    def __str__(self):
        return self.job_content


class UserBacklog(BaseModel):
    """用户待办事项

    工单流程中使用，被指派或处理时同时生成一条工单
    指派或处理完成后将待办事项删除
    """
    class BacklogType(TextChoices):
        """待办事件类型"""
        device_worksheet = 'DS', '设备工单'
        event_worksheet = 'ES', '事件工单'

        # handover = 'handover', '交接班'
        # device_work_order_confirm = 'work_order_confirm', '设备工单确认'
        # device_work_order_solve = 'work_order_solve', '设备工单处理'
        # device_work_order_audit = 'work_order_audit', '设备工单审核'
        # alarm_event_confirm = 'event_confirm', '报警事件确认'
        # alarm_event_solve = 'event_solve', '报警事件处理'
        # alarm_event_audit = 'event_audit', '报警事件审核'

    object_id = models.IntegerField('待办事件对象id')
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)

    # 您有一条事件工单待处理
    # 您有一条设备工单待处理
    description = models.CharField('待办事件描述', max_length=50)
    backlog_type = models.CharField('待办事件类型', choices=BacklogType.choices, max_length=20)

    class Meta:
        verbose_name = '用户待办事项'
        verbose_name_plural = verbose_name
        db_table = 'tb_user_backlog'
