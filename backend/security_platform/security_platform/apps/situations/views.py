import datetime
from collections import OrderedDict

from django.db import connection
from django.db.models import Count

from security_platform import config_parser
from security_platform.utils import views
from security_platform.utils.filters import CustomDjangoFilterBackend
from devices.filter import DeviceObjectPermissionsFilter
from devices.models import DeviceInfo
from situations import serializers, aggregates
from situations.filter import CameraFilter, FlightFilter
from situations.models import ResourceInfo, FlightResource, PassageWayCarPassThrough


class ResourceView(views.NoPaginationListCustomAPIView):
    """态势资源视图"""

    aggregate_classes = ()
    resource_type = None
    serializer_class = serializers.ResourceInfoSerializer
    queryset = ResourceInfo.objects.all()

    def get_queryset(self):
        """根据资源类型过滤查询集"""
        return self.queryset.filter(resource_type=self.resource_type).only('name', 'resource_type')

    def get_resource_type(self):
        """获取资源类型

        子类必须定义类属性resource_type 或覆盖此方法

        Raises:
            AssertionError: 子类未定义resource_type时抛出该异常
        """
        assert self.resource_type is not None, (
                "'%s' should either include a `resource_type` attribute, "
                "or override the `get_resource_type()` method." % self.__class__.__name__
        )

        return self.resource_type

    def get(self, *args, **kwargs):
        """获取态势资源数据列表

        遍历aggregate_classes对象调用add_data方法添加额外的分析字段数据
        """
        response = super().get(*args, **kwargs)

        for aggregate_class in list(self.aggregate_classes):
            response = aggregate_class().add_data(response, self.get_resource_type())

        return response


class PassagewayView(ResourceView):
    """出入口信息接口"""

    aggregate_classes = (aggregates.PeopleCountingAggregates, )
    resource_type = ResourceInfo.ResourceType.PASSAGEWAY


class CheckInCounterView(ResourceView):
    """值机柜台列表信息接口"""

    aggregate_classes = (aggregates.QueueNumberAggregates, )
    resource_type = ResourceInfo.ResourceType.COUNTER


class SecurityCheckView(ResourceView):
    """安检口列表信息接口"""

    aggregate_classes = (aggregates.QueueNumberAggregates, aggregates.PeopleCountingAggregates)
    resource_type = ResourceInfo.ResourceType.SECURITY


class BoardingGateView(ResourceView):
    """登机口信息"""

    aggregate_classes = (aggregates.PeopleCountingAggregates, )
    resource_type = ResourceInfo.ResourceType.BOARDING


class ReverseChannelView(ResourceView):
    """反向通道信息"""

    aggregate_classes = (aggregates.PeopleCountingAggregates, )
    resource_type = ResourceInfo.ResourceType.REVERSE


class PlacementView(ResourceView):
    """机位视图"""

    aggregate_classes = (aggregates.PlacementAggregates, )
    resource_type = ResourceInfo.ResourceType.PLACEMENT


class FlightResourceView(views.ListCustomAPIView):
    """航班信息"""

    filter_backends = (CustomDjangoFilterBackend,)
    filter_class = FlightFilter
    serializer_class = serializers.FlightSerializer
    queryset = FlightResource.objects.all().only(
        'resource_id',
        'resource__name',
        'resource__resource_type',
        'flight__flight_number',
        'plan_start_time',
        'plan_end_time',
        'actual_start_time',
        'actual_end_time'
    ).select_related('resource', 'flight').order_by('-id')


class CarPassThroughView(views.ListCustomAPIView):
    """道口车辆出入信息"""

    serializer_class = serializers.CarPassThroughSerializer
    queryset = PassageWayCarPassThrough.objects.all().order_by('-id')

    def aggregate_data_process(self, aggregate_data):
        """统计数据处理"""
        data = OrderedDict()
        data['enter_count'] = 0
        data['exit_count'] = 0

        for group in aggregate_data:
            if group['direction'] == PassageWayCarPassThrough.DirectionType.ENTRANCE:
                data['enter_count'] += group['count']
            else:
                data['exit_count'] += group['count']

        current_count = data['enter_count'] - data['exit_count']
        data['current_count'] = current_count if current_count > 0 else 0

        return data

    def get_aggregate_data_by_date(self, date):
        """根据时间获取统计数据

        根据日期进行过滤并根据出入方向进行分组查询

        Args:
            date: 统计时间

        Returns:
            aggregate_data: 统计数据
        """
        aggregate_data = PassageWayCarPassThrough.objects.values('direction').annotate(
            count=Count('id')).filter(
            passage_time__gte=date,
            passage_time__lt=date + datetime.timedelta(days=1)
        )

        return aggregate_data

    def get(self, request, *args, **kwargs):
        """获取道口车辆信息"""
        response = super().list(request, *args, **kwargs)

        # 添加统计数据
        aggregate_data = self.get_aggregate_data_by_date(datetime.datetime.now().date())
        response.data['aggregate'] = self.aggregate_data_process(aggregate_data)

        return response


class RunDayView(views.CustomGenericAPIView):
    """获取运行天数"""

    def get_database_create_time(self):
        """获取数据库创建时间"""
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT CREATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='
                           f'"{config_parser.get("MYSQL", "MYSQL_NAME")}" AND TABLE_NAME="django_migrations";')

            return cursor.fetchall()[0][0]

    def get(self, _):
        """获取运行时间"""
        run_day = (datetime.datetime.now() - self.get_database_create_time()).days + 1
        return self.success_response(data={'run_day': run_day})


class CameraView(views.NoPaginationListCustomAPIView):
    """摄像机列表"""

    filter_backends = (DeviceObjectPermissionsFilter, CustomDjangoFilterBackend)
    filter_class = CameraFilter
    serializer_class = serializers.CameraDeviceSerializer
    queryset = DeviceInfo.objects.filter(device_type=DeviceInfo.DeviceType.CAMERA).only(
        'resource_id',
        'resource__name',
        'resource__resource_type',
        'device_name',
        'device_code',
        'cameradevice__flow_address',
    ).select_related('resource', 'cameradevice').order_by('resource')
