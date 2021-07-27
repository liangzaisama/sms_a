from rest_framework import serializers

from configurations.models import GisLayer, GisMap
from security_platform.utils.serializer import CustomSerializer, CustomModelSerializer


class ConfigSerializer(CustomSerializer):
    """系统配置序列化器"""

    security_speed = serializers.IntegerField(label='安检速度', max_value=300, min_value=10)
    event_delete = serializers.IntegerField(label='报警事件保留时间', max_value=365, min_value=30)
    event_close_1 = serializers.IntegerField(label='1级报警事件自动关闭时间', max_value=100, min_value=1)
    event_close_2 = serializers.IntegerField(label='2级报警事件自动关闭时间', max_value=100, min_value=1)
    event_close_3 = serializers.IntegerField(label='3级报警事件自动关闭时间', max_value=100, min_value=1)
    event_close_4 = serializers.IntegerField(label='4级报警事件自动关闭时间', max_value=100, min_value=1)


class GisLayerSerializer(CustomModelSerializer):
    """gis图层获取"""

    class Meta:
        model = GisLayer
        fields = ('layer_id', 'layer_name', 'layer_type', 'resource_name', 'remark')


class GisMapSerializer(CustomModelSerializer):
    """gis地图校验"""

    class Meta:
        model = GisMap
        fields = ('map_class', 'map_name', 'map_type')
