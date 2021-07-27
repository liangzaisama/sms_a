"""
视频分析聚合统计数据集成：
给response中的子对象增加排队、人数统计、航班等数据

Examples：
    class PassagewayView(ResourceView):
        aggregate_classes = (aggregates.PeopleCountingAggregates, )
        resource_type = ResourceInfo.ResourceType.PASSAGEWAY

"""
from datetime import timedelta, datetime
from collections import OrderedDict

from django.db.models.aggregates import Sum

from security_platform.utils.commen import datetime_to_str
from situations.models import FlightResource
from events.models import CameraLineUpRecord, PeopleCountingRecord


class BaseAggregates:
    """数据集成接口"""

    def add_data(self, response, resource_type):
        """在原response数据中添加其他字段

        子类继承时，必须实现该方法

        Args:
            response: 原始api响应
            resource_type: 资源类型

        Returns:
            添加了额外字段的响应对象
        """
        raise NotImplementedError("method .add_data() must be Implemented.")


class GenericAggregates(BaseAggregates):
    """通用数据添加模版类"""

    @property
    def current_time(self):
        """当前时间"""
        if not hasattr(self, '_current_time'):
            self._current_time = datetime.now()

        return self._current_time

    def load_data_from_db(self, resource_type):
        """从数据库中加载数据

        子类在该函数中编写执行sql查询获取数据的代码

        Args:
            resource_type: 资源类型，sql查询时的过滤条件

        Returns:
            从数据库中读取的数据

        Raises:
            NotImplementedError: 子类未重写时抛出该异常
        """
        raise NotImplementedError("method .load_data_from_db() must be Implemented.")

    def _add_data(self, db_data, response_data):
        """对响应中的每个数据对象添加字段

        子类需要重写该方法，添加自己想要的字段及代码逻辑

        Args:
            db_data: 数据库数据
            response_data: 响应中的每个数据对象

        Raises:
            NotImplementedError: 未重写时抛出异常
        """
        raise NotImplementedError("method ._add_data() must be Implemented.")

    def add_data(self, response, resource_type):
        """在原始响应中添加字段"""
        db_data = self.load_data_from_db(resource_type)
        for response_data in response.data:
            if not isinstance(response_data, OrderedDict):
                break

            self._add_data(db_data, response_data)

        return response


class QueueNumberAggregates(GenericAggregates):
    """排队人数"""

    def load_data_from_db(self, resource_type):
        """排队聚合数据加载"""
        return CameraLineUpRecord.objects.filter(
            camera__resource__resource_type=resource_type,
            detection_time__gte=self.current_time - timedelta(minutes=CameraLineUpRecord.expire)
        ).values('current_queue_number', 'camera__resource__id')

    def _add_data(self, db_data, response_data):
        """添加排队字段"""
        response_data['current_queue_number'] = 0

        for row_data in db_data:
            if row_data['camera__resource__id'] == response_data['resource_id']:
                response_data['current_queue_number'] = row_data['current_queue_number']
                break


class PeopleCountingAggregates(GenericAggregates):
    """人数统计"""

    def load_data_from_db(self, resource_type):
        """加载人数统计聚合数据"""
        return PeopleCountingRecord.objects.filter(
            camera__resource__resource_type=resource_type,
            statistical_time__gte=self.current_time.date()
        ).values('camera__resource__id').annotate(total_people=Sum('total_people'))

    def _add_data(self, db_data, response_data):
        """添加总人数和速度"""
        response_data['total_people'] = 0
        response_data['speed'] = 0

        for row_data in db_data:
            if row_data['camera__resource__id'] == response_data['resource_id']:
                response_data['total_people'] = row_data['total_people']
                response_data['speed'] = self.get_speed(row_data)
                break

    def get_speed(self, resource_data):
        """获取人员通过速度

        平均每小时的速度

        Args:
            resource_data: 资源对应的统计数据

        Returns:
            安检速度 整型,每小时为单位
        """
        hour = self.current_time.hour + (self.current_time.minute / 60)
        if hour > 0:
            return int(resource_data['total_people'] // hour)

        return resource_data['total_people']


class PlacementAggregates(GenericAggregates):
    """机位数据"""

    def load_data_from_db(self, resource_type):
        """加载航班数据

        判断机位是否占用的标准:
        1 航班日期为今天
        2 使用状态为y
        3 实际开始使用时间存在
        4 实际结束使用时间不存在（如果存在结束使用时间那么代表机位使用已经结束）
        """
        data = FlightResource.objects.filter(
            resource__resource_type=resource_type,
            actual_start_time__isnull=False,
            actual_end_time__isnull=True,
            is_using=True,
            flight__execution_date=datetime.now().date()
        ).order_by('-actual_start_time')

        return data

    def _add_data(self, db_data, response_data):
        """添加机位状态和航班号"""
        response_data['is_using'] = False

        for flight_resource in db_data:
            if flight_resource.resource_id == response_data['resource_id']:
                response_data['is_using'] = True
                response_data['flight_id'] = flight_resource.flight.id
                response_data['flight_number'] = flight_resource.flight.flight_number
                response_data['plan_start_time'] = datetime_to_str(flight_resource.plan_start_time)
                response_data['plan_end_time'] = datetime_to_str(flight_resource.plan_end_time)
                response_data['actual_start_time'] = datetime_to_str(flight_resource.actual_start_time)
                response_data['actual_end_time'] = datetime_to_str(flight_resource.actual_end_time)
                break
