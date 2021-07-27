"""安保事件模块模型类

模型类配置包括字段，表明，外键，索引等配置
"""
import datetime
import time
import random
from collections import OrderedDict

from django.db import models

from users.models import User
from devices.models import DeviceInfo, ResourceInfo, CameraDevice
from security_platform.utils.models import BaseModel
from security_platform import TextChoices, IntegerChoices
from situations.models import FlightInfo


class AlarmEvent(BaseModel):
    """基础报警事件

    包含人工报警事件、子系统设备报警事件的公共基础信息字段
    便于查询列表和相关统计
    """

    class EventType(IntegerChoices):
        """事件状态枚举"""
        DEVICE = 1, '自动上报'
        ARTIFICIAL = 2, '人工上报'
        TRAILER = 3, '预警'

    # create_time = models.DateTimeField(verbose_name="创建时间")
    event_name = models.CharField('事件名称', max_length=50)
    event_type = models.SmallIntegerField('事件类型', choices=EventType.choices, default=1)
    event_code = models.CharField('事件编号', max_length=50, unique=True)
    alarm_time = models.DateTimeField('报警时间')
    area_code = models.CharField('所属区域', blank=True, max_length=20)
    floor_code = models.CharField('所属楼层', blank=True, max_length=20)
    priority = models.SmallIntegerField('事件等级（1-4，1级为最高级别）', default=4, db_index=True)
    event_state = models.CharField('状态', max_length=20)
    location_detail = models.CharField('事件位置(x,y)', max_length=30, blank=True)
    event_description = models.TextField('事件描述', blank=True)

    class Meta:
        verbose_name = '基础报警事件'
        verbose_name_plural = verbose_name
        db_table = 'tb_basic_alarm_event'
        index_together = [
            ["event_type", "priority","event_state", "create_time"],
        ]

    @classmethod
    def generate_event_code(cls):
        """生成事件ID

        用于统一生成子系统报警和人工报警的事件ID
        根据A+时间戳保留4位小数拼接字段串

        Returns:
            event_code: 事件ID
        """
        return f"A{str(round(time.time(), 2)).replace('.', '')}{random.randint(10, 99)}".ljust(15, '0')

    @classmethod
    def event_type_label(cls, event_type):
        """映射事件状态为中文"""
        if event_type == cls.EventType.DEVICE:
            event_type = cls.EventType.DEVICE.label
        elif event_type == cls.EventType.ARTIFICIAL:
            event_type = cls.EventType.ARTIFICIAL.label
        elif event_type == cls.EventType.TRAILER:
            event_type = cls.EventType.TRAILER.label

        return event_type

    def __str__(self):
        return self.event_name


class DeviceAlarmEvent(AlarmEvent):
    """子系统设备报警事件

    事件确认停用，原字段及接口暂时保留
    事件报警触发->事件报警处置->事件报警解除
    """

    class EventState(TextChoices):
        """事件状态枚举"""
        UNCONFIRMED = 'unconfirmed', '待确认'  # 该状态不使用，设备报警过来后直接时待处置状态
        UNDISPOSED = 'undisposed', '待处置'
        RELIEVED = 'relieved', '已解除'

    subsystem_event_id = models.CharField('子系统事件ID', max_length=50, unique=True)
    alarm_type = models.CharField('报警类型(布控、行为识别..)', max_length=20, blank=True)
    device = models.ForeignKey(DeviceInfo, verbose_name='关联设备', on_delete=models.CASCADE)
    belong_system = models.CharField('所属系统', max_length=20)
    is_misrepresent = models.BooleanField('是否误报', null=True)
    acknowledged_user = models.CharField('确认人', blank=True, max_length=20)
    acknowledged_time = models.DateTimeField('确认时间', null=True)
    acknowledged_opinion = models.CharField('确认意见', max_length=255, blank=True)
    dispose_user = models.CharField('处置人', blank=True, max_length=20)
    dispose_time = models.DateTimeField('处置时间', null=True)
    dispose_opinion = models.CharField('处置意见', max_length=255, blank=True)
    # 审核
    audit_user = models.CharField('审核人', max_length=20, blank=True)
    audit_time = models.DateTimeField('审核时间', null=True)
    audit_opinion = models.CharField('审核意见', max_length=255, blank=True)
    # 额外字段
    pass_id = models.CharField('门禁通行证id', max_length=50, blank=True)

    WS_URL_SUFFIX = 'event'

    class Meta:
        verbose_name = '系统报警事件'
        verbose_name_plural = verbose_name
        db_table = 'tb_system_alarm_event'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['event_id'] = self.id
        message['event_name'] = self.event_name
        message['event_type'] = self.event_type
        message['event_code'] = self.event_code
        message['alarm_time'] = str(self.alarm_time)
        message['area_name'] = self.area_code
        message['floor_code'] = self.floor_code
        message['priority'] = self.priority
        message['event_state'] = self.event_state
        message['location_detail'] = self.location_detail
        message['event_description'] = self.event_description
        message['resource_id'] = self.device.resource_id
        message['resource_type'] = getattr(self.device.resource, 'resource_type', None)
        message['resource_name'] = getattr(self.device.resource, 'name', None)
        message['device_code'] = self.device.device_code
        message['gis_basic_info'] = self.device.gis_basic_info
        message['gis_field'] = self.device.gis_field

        return message

    @classmethod
    def event_state_label(cls, event_state):
        if event_state == cls.EventState.UNCONFIRMED:
            event_state = cls.EventState.UNCONFIRMED.label
        elif event_state == cls.EventState.UNDISPOSED:
            event_state = cls.EventState.UNDISPOSED.label
        elif event_state == cls.EventState.RELIEVED:
            event_state = cls.EventState.RELIEVED.label

        return event_state


class PersonAlarmEvent(AlarmEvent):
    """人工快捷上报事件"""

    class AlarmPersonType(IntegerChoices):
        """人员类型枚举"""
        PASSENGERS = 1, '公众'
        STAFF = 2, '机场人员'

    class EventState(TextChoices):
        """事件状态枚举"""
        UNAUDITED = 'unaudited', '待审核'
        AUDITED = 'audited', '已审核'

    alarm_person_name = models.CharField('报警人名称', max_length=20)
    alarm_person_type = models.SmallIntegerField('报警人类别', choices=AlarmPersonType.choices)
    alarm_person_mobile = models.CharField('报警人电话', max_length=20, blank=True)
    # 处理
    handled_user = models.CharField('处理人', max_length=20, blank=True)
    handled_time = models.DateTimeField('处理时间', null=True)
    handled_opinion = models.CharField('处理意见', max_length=255, blank=True)
    # 审核
    audit_user = models.CharField('审核人', max_length=20, blank=True)
    audit_time = models.DateTimeField('审核时间', null=True, blank=True)
    audit_opinion = models.CharField('审核意见', max_length=255, blank=True)
    # gis信息
    gis_basic_info = models.TextField('gis基础信息', blank=True)
    gis_field = models.CharField('gis点位信息(x,y)', blank=True, max_length=100)

    class Meta:
        verbose_name = '人工报警事件'
        verbose_name_plural = verbose_name
        db_table = 'tb_person_alarm_event'

    @classmethod
    def event_state_label(cls, event_state):
        if event_state == cls.EventState.UNAUDITED:
            event_state = cls.EventState.UNAUDITED.label
        elif event_state == cls.EventState.AUDITED:
            event_state = cls.EventState.AUDITED.label
        return event_state


class EventWorkSheet(BaseModel):
    """事件工单"""

    class SheetState(TextChoices):
        """工单状态枚举"""
        UNAUDITED = 'unaudited', '待审核'
        CLOSED = 'closed', '已关闭'

    work_sheet_code = models.CharField('工单编号', max_length=20, unique=True)
    alarm_event = models.ForeignKey(AlarmEvent, verbose_name='事件', on_delete=models.CASCADE)
    dispose_user = models.ForeignKey(User, verbose_name='处置人', on_delete=models.PROTECT, null=True)
    sheet_state = models.CharField('工单状态', max_length=20, choices=SheetState.choices, default='unaudited')
    # 销单
    close_user = models.CharField('销单人', max_length=20, blank=True)
    close_time = models.DateTimeField('销单时间', null=True, blank=True)
    close_opinion = models.CharField('销单备注', max_length=255, blank=True)

    @classmethod
    def generate_work_sheet_code(cls):
        """生成工单编号

        用于统一生成的工单编号
        根据E+时间戳保留4位小数拼接字段串

        Returns:
            work_sheet_code: 工单编号
        """
        return 'E{0}'.format(str(round(time.time(), 4)).replace('.', ''))

    @property
    def event_type(self):
        """事件类型"""
        return self.alarm_event.event_type

    def __str__(self):
        return self.work_sheet_code

    class Meta:
        verbose_name = '事件工单'
        verbose_name_plural = verbose_name
        db_table = 'tb_event_work_sheet'


class DeviceAlarmEventPicture(models.Model):
    """子系统设备报警事件图片"""

    event = models.ForeignKey(DeviceAlarmEvent, on_delete=models.CASCADE, verbose_name='报警事件')
    address = models.CharField('报警图片地址', max_length=100)

    class Meta:
        verbose_name = '事件报警图片'
        verbose_name_plural = verbose_name
        db_table = 'tb_event_picture'


class DeviceAlarmEventCamera(models.Model):
    """子系统设备报警事件关联摄像机"""

    event = models.ForeignKey(DeviceAlarmEvent, on_delete=models.CASCADE, verbose_name='报警事件')
    code = models.CharField('摄像机编码', max_length=50)
    preset = models.CharField('摄像机预置位', max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = '事件关联摄像机'
        verbose_name_plural = verbose_name
        db_table = 'tb_event_relate_camera'


class AnalysisAlarmEventBaseModel(BaseModel):
    """视频分析系统报警字段"""

    resource = models.ForeignKey(ResourceInfo, null=True, blank=True, verbose_name='关联资源', on_delete=models.CASCADE)
    event = models.OneToOneField(DeviceAlarmEvent, verbose_name='关联设备报警事件', on_delete=models.CASCADE)
    alarm_image_url = models.CharField('报警图片地址', max_length=200, blank=True)

    class Meta:
        abstract = True

    @property
    def resource_type(self):
        return self.resource.resource_type if self.resource else None

    @property
    def resource_name(self):
        return self.resource.name if self.resource else None


class DeployAlarmRecord(AnalysisAlarmEventBaseModel):
    """实时布控人员报警记录"""

    class DbType(TextChoices):
        """库类型枚举"""
        BLACK = 'black', '黑名单'
        WHITE = 'white', '白名单'
        MAJOR = 'major', '重点人群库'
        VIP = 'vip', 'VIP'

    person_db_image_url = models.CharField('人像库图片地址', max_length=200)
    score = models.FloatField('相似度')
    name = models.CharField('姓名', blank=True, max_length=64)
    sex = models.CharField('性别', blank=True, max_length=5)
    born = models.CharField('出生日期', blank=True, max_length=35)
    type = models.CharField('证件类型', blank=True, max_length=15)
    number = models.CharField('证件号', blank=True, max_length=30)
    country = models.CharField('国家', blank=True, max_length=64)
    city = models.CharField('城市', blank=True, max_length=64)
    db_name = models.CharField('库名称', blank=True, max_length=64)
    monitor_type = models.CharField('布控类型', blank=True, max_length=11)
    db_type = models.CharField('库类型', blank=True, max_length=20)
    level = models.CharField('库等级', blank=True, max_length=6)
    customType = models.BooleanField('自定义库类型')

    # ws消息地址
    WS_URL_SUFFIX = 'deploy_alarm'

    class Meta:
        verbose_name = '实时布控人员报警记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_deploy_alarm_record'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        # 区分哪种资源
        message['resource_id'] = self.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['event_id'] = self.event_id
        message['alarm_time'] = str(self.event.alarm_time)
        message['person_db_image_url'] = self.person_db_image_url
        message['alarm_image_url'] = self.alarm_image_url
        message['score'] = self.score
        message['name'] = self.name
        message['sex'] = self.sex
        message['type'] = self.type
        message['number'] = self.number
        message['country'] = self.country
        message['city'] = self.city
        message['db_name'] = self.db_name
        message['monitor_type'] = self.monitor_type
        message['db_type'] = self.db_type
        message['level'] = self.level
        message['customType'] = self.customType

        return message


# noinspection PyUnresolvedReferences
class PersonDensityRecord(AnalysisAlarmEventBaseModel):
    """密度报警记录 3"""

    total_people_number = models.IntegerField('报警人数')

    # ws消息地址
    WS_URL_SUFFIX = 'density_alarm'

    class Meta:
        verbose_name = '密度报警记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_density_alarm_record'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['resource_id'] = self.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['alarm_image_url'] = self.alarm_image_url
        message['alarm_time'] = str(self.event.alarm_time)
        message['event_id'] = self.event_id
        message['priority'] = self.event.priority
        message['total_people_number'] = self.total_people_number
        message['device_name'] = self.event.device.device_name
        message['device_code'] = self.event.device.device_code
        message['flow_address'] = self.event.device.cameradevice.flow_address

        return message


class BehaviorAlarmRecord(AnalysisAlarmEventBaseModel):
    """行为识别报警记录"""

    # ws消息地址
    # WS_URL_SUFFIX = 'behavior_alarm'

    class Meta:
        verbose_name = '行为识别报警记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_behavior_alarm_record'

    # @property
    # def ws_message(self):
    #     """触发报警websocket消息构造"""
    #     message = OrderedDict()
    #     message['resource_id'] = self.resource_id
    #     message['resource_name'] = self.resource.name
    #     message['resource_type'] = self.resource.resource_type
    #
    #     message['event_id'] = self.event_id
    #     message['event_name'] = self.event.event_name
    #     message['alarm_image_url'] = self.alarm_image_url
    #     message['alarm_time'] = str(self.event.alarm_time)
    #
    #     return message


class PostureAlarmRecord(AnalysisAlarmEventBaseModel):
    """姿态动作识别报警记录"""

    class PostureType(IntegerChoices):
        """姿态动作映射"""
        RUN = 1, '奔跑'
        FIGHT = 2, '打架'
        FALL = 3, '倒地'
        SQUATS = 4, '下蹲'
        CALL = 5, '打电话'

    action_type = models.SmallIntegerField(choices=PostureType.choices, verbose_name='姿态动作事件类型')

    # ws消息地址
    WS_URL_SUFFIX = 'posture_alarm'

    class Meta:
        verbose_name = '姿态动作报警记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_posture_alarm_record'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['resource_id'] = self.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['event_id'] = self.event_id
        message['event_name'] = self.event.event_name
        message['alarm_image_url'] = self.alarm_image_url
        message['alarm_time'] = str(self.event.alarm_time)

        return message


class PlaceAlarmRecord(AnalysisAlarmEventBaseModel):
    """机位报警记录"""

    # ws消息地址
    WS_URL_SUFFIX = 'place_alarm'

    class Meta:
        verbose_name = '机位报警记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_place_alarm_record'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['resource_id'] = self.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['event_id'] = self.event_id
        message['event_name'] = self.event.event_name
        message['alarm_image_url'] = self.alarm_image_url
        message['alarm_time'] = str(self.event.alarm_time)

        return message


class AnalysisCurrentEventBaseModel(BaseModel):
    camera = models.ForeignKey(DeviceInfo, verbose_name='摄像机设备', on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @property
    def resource_type(self):
        return self.camera.resource.resource_type if self.camera.resource else None

    @property
    def resource_name(self):
        return self.camera.resource.name if self.camera.resource else None


class DeployPersonSnapRecord(AnalysisCurrentEventBaseModel):
    """布控人员抓拍 2"""

    snap_image_url = models.CharField('抓拍图片地址', max_length=200)
    snap_time = models.DateTimeField('抓拍时间')

    # ws消息地址
    WS_URL_SUFFIX = 'deploy_snap'

    class Meta:
        verbose_name = '实时布控人员抓拍'
        verbose_name_plural = verbose_name
        db_table = 'tb_deploy_snap_record'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['resource_id'] = self.camera.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['snap_image_url'] = self.snap_image_url
        message['snap_time'] = str(self.snap_time)

        return message


class CameraLineUpRecord(AnalysisCurrentEventBaseModel):
    """排队记录"""

    camera = models.OneToOneField(DeviceInfo, verbose_name='摄像机', on_delete=models.CASCADE)  # 重写camera，保证1对1
    detection_time = models.DateTimeField('检测时间')
    current_queue_number = models.IntegerField('当前排队人数')

    # ws消息地址
    WS_URL_SUFFIX = 'people_queue'

    # 数据有效期5分钟
    expire = 5

    # objects = CameraLineUpRecordManager()

    class Meta:
        verbose_name = '排队人数'
        verbose_name_plural = verbose_name
        db_table = 'tb_line_up_records'

    @property
    def ws_message(self):
        """实时排队websocket消息构造"""
        message = OrderedDict()
        message['resource_id'] = self.camera.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['current_queue_number'] = self.current_queue_number

        return message


class PeopleCountingRecord(AnalysisCurrentEventBaseModel):
    """实时人数统计记录

    0 点  0人
    1点   100人
    2点   180人
    3点   209人
    ...
    24时  xxx人
    """

    statistical_time = models.DateTimeField('统计时间')
    total_people = models.IntegerField('统计总人数', default=1)

    class Meta:
        verbose_name = '实时人数统计记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_people_counting_records'
        unique_together = ['camera', 'statistical_time']

    @classmethod
    def time_to_statistical_time(cls, datetime_):
        """将普通时间转化为存储的统计时间

        时间转化规则如下:
        1：整点时间，取本身时间值
        2：非整点时间，取本身时间下个小时值
        3：超过23点的时间数据处理为23点59分59秒

        Args:
            datetime_: 要转化的时间

        Returns:
            统计时间
        """
        # 统计时间参数，分秒毫秒默认为0
        statistical_kwargs = OrderedDict(year=datetime_.year, month=datetime_.month, day=datetime_.day,
            hour=datetime_.hour)

        if datetime_.minute != 0 or datetime_.second != 0 or datetime_.microsecond != 0:
            # 非整点时间
            if datetime_.hour != 23:
                statistical_kwargs['hour'] += 1
            else:
                # 24点 == 23点59分59秒
                statistical_kwargs['minute'] = 59
                statistical_kwargs['second'] = 59

        return datetime.datetime(**statistical_kwargs)


class PlaceSafeguardRecord(AnalysisCurrentEventBaseModel):
    """机位保障记录"""

    safeguard_name = models.CharField('保障节点名称', max_length=50)
    safeguard_time = models.DateTimeField('保障节点时间')
    safeguard_image_url = models.CharField('机位保障图片地址', max_length=200, blank=True)
    flight = models.ForeignKey(FlightInfo, on_delete=models.CASCADE, null=True, blank=True)

    # ws消息地址
    WS_URL_SUFFIX = 'place_safeguard'

    class Meta:
        verbose_name = '机位保障记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_place_safeguard_record'

    @property
    def ws_message(self):
        """触发报警websocket消息构造"""
        message = OrderedDict()
        message['resource_id'] = self.camera.resource_id
        message['resource_type'] = self.resource_type
        message['resource_name'] = self.resource_name
        message['safeguard_name'] = self.safeguard_name
        message['safeguard_time'] = str(self.safeguard_time)
        message['flight_number'] = getattr(self.flight, 'flight_number', None)

        return message
