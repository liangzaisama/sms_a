"""
态势资源序列化器
"""
from rest_framework import serializers

from devices.models import DeviceInfo
from situations.models import ResourceInfo, PassageWayCarPassThrough, FlightResource
from security_platform.utils.serializer import CustomModelSerializer, CustomCharField


class ResourceInfoSerializer(CustomModelSerializer):
    """基础资源信息查询序列化器"""

    class Meta:
        model = ResourceInfo
        fields = ['resource_id', 'resource_name', 'resource_type']
        extra_kwargs = {
            'resource_name': {'source': 'name'},
            'resource_id': {'source': 'id'},
        }


class CarPassThroughSerializer(CustomModelSerializer):
    """获取道口车辆信息序列化器"""

    class Meta:
        model = PassageWayCarPassThrough
        fields = [
            'car_number_image_url', 'car_number', 'passageway_name', 'direction',
            'passage_time', 'passageway_device_code'
        ]


class FlightSerializer(CustomModelSerializer):
    """航班信息"""

    resource_name = serializers.CharField(source='resource.name')
    resource_type = serializers.CharField(source='resource.resource_type')
    terminal_number = serializers.CharField(source='resource.terminal_number')
    nature = serializers.CharField(source='resource.nature')
    exit_number = serializers.CharField(source='resource.exit_number')
    flight_number = serializers.CharField(source='flight.flight_number')

    class Meta:
        model = FlightResource
        fields = [
            'resource_id', 'resource_name', 'resource_type', 'terminal_number', 'nature',
            'exit_number', 'flight_number', 'plan_start_time', 'plan_end_time',
            'actual_start_time', 'actual_end_time'
        ]


class CameraDeviceSerializer(CustomModelSerializer):
    """摄像机设备序列化器"""

    resource_name = CustomCharField(source='resource.name')
    resource_type = CustomCharField(source='resource.resource_type')
    flow_address = CustomCharField(source='cameradevice.flow_address')

    class Meta:
        model = DeviceInfo
        fields = ['device_name', 'device_code', 'flow_address', 'resource_name', 'resource_type', 'resource_id']
