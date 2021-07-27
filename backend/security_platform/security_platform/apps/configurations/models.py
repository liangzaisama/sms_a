"""
系统配置模型类
"""
from django.db import models

from security_platform import TextChoices
from security_platform.utils.models import BaseModel


class SystemConfig(models.Model):
    """用户IP白名单"""

    class ConfigKey(TextChoices):
        """配置列表"""
        EVENT_CLOSE_1 = 'event_close_1', '1级报警事件自动关闭(单位:小时)'
        EVENT_CLOSE_2 = 'event_close_2', '2级报警事件自动关闭(单位:小时)'
        EVENT_CLOSE_3 = 'event_close_3', '3级报警事件自动关闭(单位:小时)'
        EVENT_CLOSE_4 = 'event_close_4', '4级报警事件自动关闭(单位:小时)'
        SECURITY_SPEED = 'security_speed', '安检速度(单位:人/小时)'
        EVENT_DELETE = 'event_delete', '报警事件删除(单位:天)'
        ANALYSIS_ALARM = 'analysis_alarm_delete', '视频分析报警删除(单位:天)'
        SUBSYSTEM_CURRENT = 'subsystem_current_delete', '子系统实时消息删除(单位:天)'
        ANALYSIS_CURRENT = 'analysis_current_delete', '视频分析实时消息删除(单位:天)'

    config_key = models.CharField('系统配置名称', unique=True, max_length=50, choices=ConfigKey.choices)
    config_value = models.CharField('系统配置值', max_length=100)
    is_exposed = models.BooleanField('是否暴露给用户', default=True)

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        db_table = 'tb_system_config'

    @classmethod
    def config_data_init(cls):
        """创建初始化数据"""
        # 安检速度，默认30, 单位:人/小时
        cls.objects.get_or_create(config_key=cls.ConfigKey.SECURITY_SPEED, defaults={'config_value': 30})

        # 报警事件删除 默认365天 单位:天
        cls.objects.get_or_create(config_key=cls.ConfigKey.EVENT_DELETE, defaults={'config_value': 365})

        # 报警事件自动关闭(不可生成事件工单) 默认1小时 单位:小时
        cls.objects.get_or_create(config_key=cls.ConfigKey.EVENT_CLOSE_1, defaults={'config_value': 1})
        cls.objects.get_or_create(config_key=cls.ConfigKey.EVENT_CLOSE_2, defaults={'config_value': 1})
        cls.objects.get_or_create(config_key=cls.ConfigKey.EVENT_CLOSE_3, defaults={'config_value': 1})
        cls.objects.get_or_create(config_key=cls.ConfigKey.EVENT_CLOSE_4, defaults={'config_value': 1})

        # 子系统实时消息删除，航班，道口车辆, 365天
        cls.objects.get_or_create(config_key=cls.ConfigKey.SUBSYSTEM_CURRENT,
                                  defaults={'config_value': 365, 'is_exposed': False})

        # 视频分析报警删除 60天
        cls.objects.get_or_create(config_key=cls.ConfigKey.ANALYSIS_ALARM,
                                  defaults={'config_value': 60, 'is_exposed': False})

        # 视频分析实时消息删除 60天
        cls.objects.get_or_create(config_key=cls.ConfigKey.ANALYSIS_CURRENT,
                                  defaults={'config_value': 60, 'is_exposed': False})

        # 删除不存在的配置
        for config in cls.objects.all():
            if config.config_key not in cls.ConfigKey.values:
                config.delete()

    @property
    def value(self):
        """将配置值字符串转为原始格式

        比如将'1' > 1
        """
        return eval(self.config_value)


class GisMap(BaseModel):
    """gis地图信息"""

    map_id = models.IntegerField(primary_key=True, verbose_name="地图id")
    map_class = models.CharField(verbose_name="大区域", max_length=100)
    map_name = models.CharField(verbose_name="小区域", max_length=100)
    map_type = models.CharField(verbose_name="设备类型", max_length=100)

    class Meta:
        verbose_name = 'gis地图'
        verbose_name_plural = verbose_name
        db_table = 'tb_gis_map'

    def __str__(self):
        return str(self.map_id)


class GisLayer(BaseModel):
    """gis图层信息"""

    layer_id = models.IntegerField(primary_key=True, verbose_name="图层id")
    layer_name = models.CharField(verbose_name="图层名称", max_length=100)
    layer_type = models.CharField(verbose_name="图层类型", max_length=100)
    resource_name = models.CharField(verbose_name="资源信息", max_length=200)
    remark = models.CharField(verbose_name="备注", max_length=200, blank=True)
    map = models.ForeignKey(GisMap, on_delete=models.CASCADE, verbose_name='关联地图')

    class Meta:
        verbose_name = 'gis图层'
        verbose_name_plural = verbose_name
        db_table = 'tb_gis_layer'


class GisPoint(BaseModel):
    """gis点位信息"""

    system_code = models.CharField(max_length=200, null=True, blank=True, verbose_name='cad名称')
    object_id = models.CharField(max_length=200, null=True, blank=True, verbose_name='cadID')
    dev_guid = models.CharField(max_length=200, null=True, blank=True, unique=True, verbose_name='设备id')
    map_id = models.CharField(max_length=200, null=True, blank=True, verbose_name='gis地图id')
    layer_id = models.CharField(max_length=200, null=True, blank=True, verbose_name='gis图层id')
    floor_id = models.CharField(max_length=200, null=True, blank=True, verbose_name='楼层')
    dev_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='设备名')
    cad_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='cad图纸工程编码')
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name='备注')
    dev_type = models.CharField(max_length=200, null=True, blank=True, verbose_name='设备类型')
    dev_manu = models.CharField(max_length=200, null=True, blank=True, verbose_name='厂商')
    camera_ip = models.CharField(max_length=200, null=True, blank=True, verbose_name='相机ip')
    x = models.CharField(max_length=200, null=True, blank=True, verbose_name='x点位')
    y = models.CharField(max_length=200, null=True, blank=True, verbose_name='y点位')
    date_time = models.CharField(max_length=200, null=True, blank=True, verbose_name='创建时间')

    class Meta:
        verbose_name = 'gis点位信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_gis_point'
