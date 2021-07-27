import time
from collections import OrderedDict

from django.db import models

from users.models import User, Department
from situations.models import ResourceInfo
from security_platform import TextChoices, IntegerChoices
from security_platform.utils.models import BaseModel, FilterIsDeletedManager


class DevicePermissionsMixin(models.Model):
    """设备权限混入类

    用于给设备类增加多对多关联及相关权限的校验

    users：关联部门员工或领导的设备权限，部门员工只有跟自身用户关联的设备权限
    department：关联部门的设备权限，部门领导拥有关联部门下的所有设备权限
    """

    users = models.ManyToManyField(
        User,
        verbose_name='关联用户设备权限',
        blank=True,
        related_name="device_set",
        related_query_name="devices"
    )

    departments = models.ManyToManyField(
        Department,
        verbose_name='关联部门设备权限',
        blank=True,
        related_name="device_set",
        related_query_name="devices"
    )

    def is_belong_department(self, department):
        """判断设备是否属于这个部门"""
        return department in self.departments.all()

    def _is_belong_user(self, user):
        """判断设备是否属于这个用户"""
        return user in self.users.all() and self.is_belong_department(user.department)

    def is_belong_user(self, user):
        """判断用户是否拥有这个设备的权限"""
        if user.is_superuser:
            return True

        if not user.is_active:
            return False

        if user.is_leader:
            # 部门领导
            return self.is_belong_department(user.department)
        else:
            # 部门员工
            return self._is_belong_user(user)

    class Meta:
        abstract = True


class DeviceManager(FilterIsDeletedManager):
    """自定义设备模型类查询Manager"""

    @property
    def simple_info(self):
        """快速查询设备信息"""
        device_data = self.all().values('id', 'device_name')

        return device_data


class DeviceInfo(BaseModel, DevicePermissionsMixin):
    """设备信息

    设备故障维修流程

    设备处于故障或故障恢复时可生成故障维修工单

    MQ通知设备故障
    故障->故障
    正常->故障
    故障恢复->故障

    MQ通知设备正常

    判断原始设备状态
    1.故障
    无工单->正常
    工单执行中->故障恢复
    工单关闭->正常

    2.故障恢复
    无工单->正常
    工单执行中->故障恢复
    工单关闭->正常

    3.正常
    正常->正常
    """
    FREQUENT_MAINTENANCE_COUNT = 3

    class DeviceState(TextChoices):
        NORMAL = 'normal', '正常'
        TROUBLE_OPEN = 'trouble_open', '故障'
        TROUBLE_OFF = 'trouble_off', '故障恢复'

    class DeviceType(TextChoices):
        CAMERA = 'cctv', '视频监控设备'
        MAINTENANCE = 'enclosure', '围界设备'
        ENTRANCE = 'access_control', '门禁设备'
        FIRE = 'fire', '消防设备'
        CONCEAL = 'alarm', '隐蔽报警设备'
        PASSAGE = 'passage_way', '道口设备'

    class BelongSystem(TextChoices):
        ANALYSIS = 'ZVAMS', '视频分析系统'
        CAMERA = 'VMS', '视频监控系统'
        ENTRANCE = 'ACS', '门禁系统'
        PASSAGE = 'CMS', '道口系统'
        MAINTENANCE = 'AIS', '围界系统'
        FIRE = 'XFHZ', '消防系统'
        CONCEAL = 'YBBJ', '隐蔽报警系统'

    class Scene(TextChoices):
        BASIC = 'basic'
        STATUS = 'status'
        INFO = 'info'

    # 实际展示区域，不做关联关系，子系统上报什么就是什么
    area_code = models.CharField('所属区域', blank=True, max_length=50)
    # 自定义区域，做关联关系
    resource = models.ForeignKey(ResourceInfo, null=True, blank=True, verbose_name='航站楼资源', on_delete=models.SET_NULL)

    device_type = models.CharField('类型', max_length=20, choices=DeviceType.choices)
    belong_system = models.CharField('所属系统', max_length=5, choices=BelongSystem.choices, db_index=True)
    device_state = models.CharField('设备状态', max_length=20, choices=DeviceState.choices, default='normal')
    is_deleted = models.BooleanField('逻辑删除', default=False, db_index=True)
    # 业务字段
    device_code = models.CharField('设备编码', max_length=200, unique=True)
    device_name = models.CharField('设备名称', max_length=60, db_index=True)
    device_type_id = models.CharField('设备类型编码', blank=True, max_length=36)
    device_type_id_son = models.CharField('设备子类型编码', blank=True, max_length=36)
    device_type_name = models.CharField('设备类型名称', blank=True, max_length=60)
    floor_code = models.CharField('所属楼层', blank=True, max_length=50)
    ipv4 = models.CharField('IPv4', max_length=20, blank=True)
    port = models.CharField('端口', max_length=10, blank=True)
    switches = models.CharField('交换机', max_length=100, blank=True)
    manufacturer = models.CharField('厂家', max_length=100, blank=True)
    device_model = models.CharField('型号', max_length=100, blank=True)
    trouble_message = models.CharField('设备故障信息', max_length=30, blank=True)
    trouble_time = models.DateTimeField('设备故障时间', null=True, blank=True)
    trouble_code = models.CharField('设备故障错误码', max_length=30, blank=True)
    install_location_detail = models.CharField('安装位置描述', max_length=100, blank=True)
    device_cad_code = models.CharField('安装工程码', max_length=100, blank=True)
    related_camera_code = models.CharField('关联摄像机编号', max_length=200, blank=True)
    maintenance = models.IntegerField('维修次数', default=0)
    gis_basic_info = models.CharField('gis点位信息(x,y)', blank=True, max_length=200)
    gis_field = models.CharField('gis基础信息', blank=True, max_length=200)
    installation_time = models.DateTimeField('安装时间', null=True, blank=True)
    initial_image = models.TextField('初始图片', null=True, blank=True)
    # 使用寿命暂定默认三年
    service_life = models.IntegerField('使用寿命', blank=True, default=3)
    # 围界主机、门禁主机接口模块等
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='设备主机',
                               related_name='subs')

    # 过滤逻辑删除
    objects = DeviceManager()
    # 原始查询, 不过滤逻辑删除
    raw_objects = models.Manager()

    WS_URL_SUFFIX = 'device_state'

    @property
    def frequent_maintenance(self):
        """是否频繁维修设备"""
        return True if self.maintenance > self.FREQUENT_MAINTENANCE_COUNT else False

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_device_info'
        index_together = [
            ["is_deleted", "device_type", "device_state"],
            ["is_deleted", "device_state"],
        ]

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['device_id'] = self.id
        message['device_state'] = self.device_state
        message['trouble_message'] = self.trouble_message
        message['trouble_time'] = str(self.trouble_time)
        message['trouble_code'] = self.trouble_code
        message['gis_basic_info'] = self.gis_basic_info
        message['gis_field'] = self.gis_field
        message['device_type'] = self.device_type

        return message

    def __str__(self):
        return self.device_name

    # def device_state_check(self):
    #     pass
    # 
    # def save(self, *args, **kwargs):
    #     self.device_state_check()
    #     super().save(*args, **kwargs)


class CameraDevice(DeviceInfo):
    """摄像机设备"""

    class CameraType(IntegerChoices):
        """
        对应device_type_id_son字段
        """
        BULLET = 0, '枪机'
        PTZ = 1, '球机'
        PANORAMIC = 2, '全景相机'

    camera_type = models.CharField('摄像机类型', default='枪机', max_length=10)
    is_ptz = models.BooleanField('是否支持ptz', default=False)
    flow_address = models.CharField('视频流地址', max_length=100, blank=True)
    flow_address_second = models.CharField('第二码流地址', max_length=100, blank=True)
    # resource = models.ForeignKey(ResourceInfo, null=True, blank=True, verbose_name='航站楼资源', on_delete=models.SET_NULL)
    point_angel = models.IntegerField('指向角度', null=True, blank=True)
    visual_angel = models.IntegerField('视角', null=True, blank=True)
    cover_radius = models.IntegerField('覆盖半径', null=True, blank=True)
    install_height = models.IntegerField('安装高度', null=True, blank=True)

    class Meta:
        verbose_name = '摄象机设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_camera_device'

    def __str__(self):
        return self.device_name


class MaintenanceDevice(DeviceInfo):
    """围界设备"""

    detector_code = models.CharField('编号', max_length=20, blank=True)

    class Meta:
        verbose_name = '围界设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_maintenance_device'


class EntranceDevice(DeviceInfo):
    """门禁设备"""

    door_code = models.CharField('门代号', max_length=20, blank=True)
    door_status = models.SmallIntegerField('门状态(0开,1关)', null=True, blank=True)
    open_or_close_time = models.DateTimeField('门开启/关闭时间', null=True, blank=True)

    class Meta:
        verbose_name = '门禁设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_entrance_device'


class FireDevice(DeviceInfo):
    """消防设备"""

    class Meta:
        verbose_name = '消防设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_fire_device'


class ConcealAlarmDevice(DeviceInfo):
    """隐蔽报警设备"""

    class Meta:
        verbose_name = '隐蔽报警设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_conceal_alarm_device'


class PassageWayDevice(DeviceInfo):
    """道口设备"""

    class Meta:
        verbose_name = '道口设备'
        verbose_name_plural = verbose_name
        db_table = 'tb_passage_way_device'


class WorkSheet(BaseModel):
    """工单"""

    class SheetState(TextChoices):
        """工单状态枚举"""
        ASSIGNED = 'assigned', '已指派、待维修'
        DISPOSED = 'disposed', '已处置、待审核'
        AUDITED = 'audited', '已审核'
        CLOSED = 'closed', '已关闭'

    work_sheet_code = models.CharField('工单编号', max_length=20, unique=True)
    device_info = models.ForeignKey(DeviceInfo, verbose_name='设备', on_delete=models.CASCADE)
    dispose_user = models.ForeignKey(User, verbose_name='处置人', on_delete=models.PROTECT, related_name='dispose_user')
    audit_user = models.ForeignKey(User, verbose_name='审核人', on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='audit_user')
    audit_opinion = models.TextField('审核意见', blank=True)
    sheet_state = models.CharField('工单状态', max_length=20, choices=SheetState.choices, default='assigned')

    @classmethod
    def generate_work_sheet_code(cls):
        """生成工单编号

        用于统一生成的工单编号
        根据G+时间戳保留4位小数拼接字段串

        Returns:
            work_sheet_code: 工单编号
        """
        return 'G{0}'.format(str(round(time.time(), 4)).replace('.', ''))

    def __str__(self):
        return self.work_sheet_code

    class Meta:
        verbose_name = '工单流程记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_work_sheet'


class DeviceMaintenanceRecords(models.Model):
    """设备维修记录

    员工维修或更换设备后提交维修记录
    """

    class AuditState(TextChoices):
        """审核状态枚举"""
        UNAUDITED = 'unaudited', '待审核'
        APPROVED = 'approved', '已通过'
        UNAPPROVED = 'unapproved', '未通过'

    device_info = models.ForeignKey(DeviceInfo, verbose_name='设备', on_delete=models.CASCADE)
    is_change_device = models.BooleanField('是否更换设备', default=False)
    operate_time = models.DateTimeField('维修时间')
    operate_person = models.CharField('维修人', max_length=20)
    operate_records = models.CharField('维修记录', max_length=50)
    note = models.CharField('备注', max_length=50, blank=True)
    image = models.TextField('图片', null=True, blank=True)
    work_sheet = models.ForeignKey(WorkSheet, verbose_name='设备维修工单', on_delete=models.CASCADE)
    audit_state = models.CharField('工单状态', max_length=20, choices=AuditState.choices, default='unaudited')

    class Meta:
        verbose_name = '设备安装维修记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_device_maintenance_records'


class DeviceStateHistory(models.Model):
    """设备状态变更记录"""

    device_info = models.ForeignKey(DeviceInfo, verbose_name='设备', on_delete=models.CASCADE)
    device_state = models.CharField('设备变更状态', max_length=20)
    state_change_time = models.DateTimeField('设备状态变更时间')

    class Meta:
        verbose_name = '设备状态记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_device_stated_history'


class DeviceGroup(BaseModel):
    """设备分组

    与设备是一对多关系，与用户是一对一关系
    """

    name = models.CharField('分组名称', max_length=50)
    description = models.TextField('分组说明', blank=True)
    user = models.ForeignKey(User, verbose_name='创建用户', on_delete=models.PROTECT)

    # 关联的设备
    devices = models.ManyToManyField(
        DeviceInfo,
        verbose_name='关联设备',
        blank=True,
        related_name="group_set",
        related_query_name="group",
    )

    class Meta:
        verbose_name = '设备分组'
        verbose_name_plural = verbose_name
        db_table = 'tb_device_group'
        unique_together = ['name', 'user']

    def __str__(self):
        return f'{self.user}-{self.name}'


class DeviceLabel(BaseModel):
    """设备标签

    与设备是多对多关系，与用户是一对一关系
    """

    name = models.CharField('标签名称', max_length=50)
    keywords = models.CharField('检索关键字', max_length=50)
    content = models.TextField('标签内容')
    color = models.CharField('标签颜色代码', max_length=10)
    user = models.ForeignKey(User, verbose_name='创建用户', on_delete=models.PROTECT)
    # default_gis_info = models.CharField('默认GIS定位', max_length=100, blank=True)

    # label.devices.filter(departments=label.user.department)

    # 关联的设备
    devices = models.ManyToManyField(
        DeviceInfo,
        verbose_name='关联设备',
        blank=True,
        related_name="label_set",
        related_query_name="label"
    )

    class Meta:
        verbose_name = '设备标签'
        verbose_name_plural = verbose_name
        db_table = 'tb_device_label'
        unique_together = ['name', 'user']

    def __str__(self):
        return f'{self.user}-{self.name}'
