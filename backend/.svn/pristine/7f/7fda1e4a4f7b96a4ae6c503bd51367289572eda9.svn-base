"""
态势资源部分自定义滤器类

Examples:
    class View:
        filter_backends = (CustomDjangoFilterBackend, )
        filter_class = CameraFilter
"""

from django_filters import rest_framework as filters

from events.models import DeployAlarmRecord
from devices.models import ResourceInfo, DeviceInfo
from situations.models import FlightResource
from security_platform.utils.exceptions import ParamError


class FlightFilter(filters.FilterSet):
    """航班过滤器"""

    resource_type = filters.CharFilter(field_name="resource__resource_type")

    class Meta:
        model = FlightResource
        fields = ['resource_type']

    def is_valid(self):
        """resource_type字段校验

        resource_type未传递时跳过

        Raises:
            ParamError: resource_type校验失败时抛出异常
        """
        resource_type = self.data.get('resource_type')
        if resource_type is None:
            return

        if resource_type not in ResourceInfo.ResourceType:
            raise ParamError(param_name='resource_type')


class CameraFilter(FlightFilter):
    """摄像机过滤器"""

    resource_name = filters.CharFilter(field_name="resource__name")
    device_name = filters.CharFilter(field_name="device_name", lookup_expr='icontains')
    device_code = filters.CharFilter(field_name="device_code", lookup_expr='icontains')

    class Meta:
        model = DeviceInfo
        fields = ['resource_type', 'device_code', 'device_name', 'resource_name']


class DeployAlarmFilter(FlightFilter):
    """布控报警过滤器"""

    class Meta(FlightFilter.Meta):
        model = DeployAlarmRecord
