"""态势相关模型类

1、航站楼内的资源表
航站楼出入口、值机柜台、安检口、安检大厅、登机口、反向通道、行李转盘

2、视频分析的实时结果及报警消息
实时消息包括（数据来源视频分析系统）：人数统计、密度、排队、实时抓拍
报警消息包括（数据来源视频监控系统）：行为识别报警、布控报警、排队阀值报警、密度阀值报警、

问题2：视频分析的报警调用webapi的接口触发报警，然后杨工那边再把报警消息给我，调用接口的时候缺少报警相关的信息
是不是安保平台可以直接从视频分析的MQ报警里面取报警信息，但是这样需要安保平台内部产生事件，
事件处理流程就跟视频监控客户端没关系了
需要安保平台人员去处理

3、航班系统消息及道口系统消息
道口车辆出入信息
航班相关信息
"""
from collections import OrderedDict

from django.db import models

from security_platform.utils.models import BaseModel
from security_platform import TextChoices, IntegerChoices


class FlightInfo(BaseModel):
    """航班基础信息"""

    class FlightFlag(TextChoices):
        """航班进出港标示"""
        ARRIVAL = 'A', '进港'
        DEPARTURE = 'D', '离港'

    # 基础信息
    fl_id = models.CharField('航班唯一标示', unique=True, max_length=10)
    ff_id = models.CharField('航班标识', null=True, blank=True, max_length=50)
    mf_id = models.CharField('主航班标识', null=True, blank=True, max_length=50)
    mf_fi = models.CharField('主航班标识2', null=True, blank=True, max_length=50)
    fl_tk = models.CharField('航班任务', null=True, blank=True, max_length=50)
    flight_number = models.CharField('航班号', max_length=20)
    company = models.CharField('航空公司标识', max_length=10)
    execution_date = models.DateField('航班执行日期(进港降落，出港起飞)')
    arrival_departure_flag = models.CharField('进出港标志（D-出港；A-进港）', max_length=1, choices=FlightFlag.choices)
    flight_property = models.CharField('航班属性（INT-国际；DOM-国内；REG-地区；MIX-混合）', max_length=10)
    flight_state = models.CharField('航班进展状态(ARR-到达；DEP-起飞；BOR-登机；POK-结束登机)', max_length=10,
                                    null=True, blank=True)
    exception_status = models.CharField('异常状态', max_length=10, null=True, blank=True)
    exception_reason_father = models.CharField('异常原因父类', max_length=10, null=True, blank=True)
    exception_reason_son = models.CharField('异常原因子类', max_length=10, null=True, blank=True)
    start_boarding_time = models.DateTimeField('开始登机时间', null=True, blank=True)
    end_boarding_time = models.DateTimeField('结束登机时间', null=True, blank=True)
    takeoff_iata = models.CharField('起飞航站（IATA码）', max_length=10, blank=True)
    stopover_iata = models.CharField('经停站（多个用逗号隔开）', max_length=20, null=True, blank=True)
    destination_iata = models.CharField('目的航站（IATA码）', max_length=10, blank=True)
    terminal_info = models.CharField('国内航站楼编号', max_length=10, null=True, blank=True)
    inter_terminal_info = models.CharField('国际航站楼编号', max_length=10, null=True, blank=True)
    # 航线信息
    plan_takeoff = models.DateTimeField('计划起飞时间', null=True, blank=True)
    plan_arrival = models.DateTimeField('计划到达时间', null=True, blank=True)
    estimate_takeoff = models.DateTimeField('预计起飞时间', null=True, blank=True)
    estimate_arrival = models.DateTimeField('预计到达时间', null=True, blank=True)
    actual_takeoff = models.DateTimeField('实际起飞时间', null=True, blank=True)
    actual_arrive = models.DateTimeField('实际到达时间', null=True, blank=True)

    class Meta:
        verbose_name = '航班信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_flight_info'

    def __str__(self):
        return self.flight_number


class ResourceInfo(BaseModel):
    """航站楼内的资源"""

    class ResourceType(TextChoices):
        """资源类型枚举"""
        PASSAGEWAY = 'passageway', '航站楼出入口'
        COUNTER = 'counter', '值机柜台'
        SECURITY = 'security', '安检口'
        BOARDING = 'boarding', '登机口'
        REVERSE = 'reverse', '反向通道'
        BAGGAGE = 'baggage', '行李转盘'
        PLACEMENT = 'placement', '机位'
        SECURITY_HALL = 'security_hall', '安检大厅'
        MAINTENANCE = 'maintenance', '围界'
        CROSSING = 'crossing', '道口'
        PARK = 'park', '停车场'

    class ResourceTypeSecond(TextChoices):
        """资源子类型枚举"""
        ENTRANCE = 'entrance', '航站楼入口'
        EXIT = 'exit', '航站楼出口'
        FAR_PLACEMENT = 'FP', '远机位'
        NEAR_PLACEMENT = 'NP', '近机位'

    # class ResourceStatus(IntegerChoices):
    #     FREE = 0, '空闲'  # 机位空闲/登机口关闭
    #     USE = 1, '使用'  # 机位使用/登机口开放

    # 关联航班信息
    flight_sys_id = models.CharField('航班系统ID', max_length=14, unique=True, blank=True, null=True)
    flight_sys_number = models.CharField('航班系统编号', max_length=16, blank=True)
    flight_sys_statue = models.CharField('航班系统状态（C-停用；O-可用）', max_length=5, blank=True)
    chinese_desc = models.CharField('中文描述', max_length=64, blank=True)
    english_desc = models.CharField('英文描述', max_length=64, blank=True)
    nature = models.CharField('属性（国际、国内、地区、混合）', max_length=10, default='国内')
    terminal_number = models.CharField('航站楼编号', max_length=5, blank=True)
    exit_number = models.CharField('到达出口号', blank=True, max_length=10)

    # 业务字段
    name = models.CharField('资源名称', max_length=20, db_index=True)
    # status = models.SmallIntegerField('状态', choices=ResourceStatus.choices, default=0)
    resource_type = models.CharField('一级资源分类', db_index=True, max_length=20,
                                     choices=ResourceType.choices)
    resource_type_sec = models.CharField('二级资源分类', db_index=True, max_length=20, blank=True,
                                         choices=ResourceTypeSecond.choices)

    flights = models.ManyToManyField(
        FlightInfo,
        verbose_name='关联航班信息',
        blank=True,
        related_name="flight_set",
        related_query_name="flights",
        through='FlightResource',
    )

    class Meta:
        verbose_name = '航站楼资源信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_resource_info'
        unique_together = ['resource_type', 'name']

    def __str__(self):
        return self.name


class FlightResource(models.Model):
    """资源关联航班信息

    登机口、转盘、机位

    1 登机口流程
    收到开始登机消息，登机口开始使用 status=开放
    1. 根据fl_id找到对应的航班号
    2. 根据fl_id找到对应的使用的登机口

    # 收到截止登机消息，登机口关闭使用 status=关闭

    2 机位流程
    收到视频分析的飞机入位消息，机位状态=使用
    根据机位使用时间查询出对应的航班号-根据航班号进行展示

    收到视频分析的飞机离位消息，机位状态=空闲

    3.转盘
    根据航班信息，展示预计即可
    """
    flight = models.ForeignKey(FlightInfo, verbose_name='航班信息', on_delete=models.CASCADE)
    resource = models.ForeignKey(ResourceInfo, verbose_name='资源信息', on_delete=models.CASCADE)
    plan_start_time = models.DateTimeField('预计开始使用时间')
    plan_end_time = models.DateTimeField('预计结束使用时间')
    actual_start_time = models.DateTimeField('实际开始使用时间', null=True, blank=True)
    actual_end_time = models.DateTimeField('实际结束使用时间', null=True, blank=True)
    is_using = models.BooleanField('是否使用中', default=False, db_index=True)

    class Meta:
        verbose_name = '航班资源信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_flight_resource'


class PassageWayCarPassThrough(BaseModel):
    """道口车辆通行信息"""

    class DirectionType(IntegerChoices):
        """出入方向枚举"""
        ENTRANCE = 0, '驶入'
        LEAVE = 1, '驶离'

    passageway_name = models.CharField('道口名称', max_length=20)
    passageway_device_code = models.CharField('道口设备编码', max_length=200)
    passage_time = models.DateTimeField('通行时间')
    car_number = models.CharField('车牌号', max_length=20)
    direction = models.SmallIntegerField('进出方向', choices=DirectionType.choices)
    car_number_image_url = models.CharField('车牌号图片地址', max_length=200, blank=True)
    car_positive_image_url = models.CharField('车辆正面图片地址', max_length=200, blank=True)
    car_bottom_image_url = models.CharField('车牌底部图片地址', max_length=200, blank=True)
    is_allowed = models.BooleanField(verbose_name='是否允许通行', default=True)

    WS_URL_SUFFIX = 'crossing_traffic'

    class Meta:
        verbose_name = '道口车辆通行信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_passage_way_car_pass_through'

    @property
    def ws_message(self):
        """实时排队websocket消息构造"""
        message = OrderedDict()
        message['resource_type'] = ResourceInfo.ResourceType.CROSSING
        message['passageway_name'] = self.passageway_name
        message['passageway_device_code'] = self.passageway_device_code
        message['passage_time'] = str(self.passage_time)
        message['car_number'] = self.car_number
        message['direction'] = self.direction
        message['car_number_image_url'] = self.car_number_image_url
        message['car_positive_image_url'] = self.car_positive_image_url
        message['car_bottom_image_url'] = self.car_bottom_image_url

        return message


class FlightCompany(models.Model):
    """航空公司"""

    second_code = models.CharField('航空公司二字码', unique=True, max_length=5)
    three_code = models.CharField('航空公司三字码', null=True, max_length=5)
    property = models.CharField('航空公司属性', null=True, max_length=5)
    ch_description = models.CharField('中文描述', null=True, max_length=40)
    inter_description = models.CharField('英文描述', null=True, max_length=40)
    country_code = models.CharField('国家代码', null=True, max_length=10)
    terminal = models.CharField('所在航站楼', null=True, max_length=10)
    company_group = models.CharField('航空公司联盟', null=True, max_length=25)

    class Meta:
        verbose_name = '航空公司'
        verbose_name_plural = verbose_name
        db_table = 'flight_company'

    def __str__(self):
        return self.ch_description


class Airport(models.Model):
    """机场信息"""

    three_code = models.CharField('机场三字码', unique=True, max_length=3)
    four_code = models.CharField('机场四字码', unique=True, max_length=4)
    property = models.CharField('机场属性', max_length=3)
    ch_description = models.CharField('中文描述', max_length=70)
    inter_description = models.CharField('英文描述', null=True, max_length=70)
    is_open = models.CharField('该通航机场是否开启(O,C)', null=True, max_length=1)
    alias = models.CharField('机场简称', null=True, max_length=10)
    country_code = models.CharField('国家代码', null=True, max_length=3)
    city_code = models.CharField('城市代码', null=True, max_length=3)
    lat = models.FloatField('机场纬度', null=True)
    lon = models.FloatField('机场经度', null=True)

    class Meta:
        verbose_name = '机场信息'
        verbose_name_plural = verbose_name
        db_table = 'airport'

    def __str__(self):
        return self.ch_description


class FlightException(models.Model):
    """航班异常"""

    errcode = models.CharField('错误码', unique=True, max_length=10)
    ch_description = models.CharField('中文错误描述', null=True, max_length=100)
    inter_description = models.CharField('英文错误描述', null=True, max_length=100)
    errcode_belong = models.CharField('所属异常原因类别', null=True, max_length=10)
    is_type = models.CharField('是否是异常原因类别 (n是,y不是)', null=True, max_length=10)
    errcode_type = models.CharField('异常原因分类', null=True, max_length=5)

    class Meta:
        verbose_name = '航班异常'
        verbose_name_plural = verbose_name
        db_table = 'flight_exception'

    def __str__(self):
        return self.ch_description
