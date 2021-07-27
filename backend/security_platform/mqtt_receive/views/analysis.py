"""视频分析报警数据处理

处理的报警有：布控、行为识别、排队、密度、姿态、机位、遗留物
"""
import datetime
from collections import OrderedDict

from django.db import transaction

from devices.models import DeviceInfo, EntranceDevice
from events.models import (
    AlarmEvent, DeviceAlarmEvent, DeployAlarmRecord, PersonDensityRecord, BehaviorAlarmRecord,
    PostureAlarmRecord, PlaceAlarmRecord
)

from core.generics import CreateLabelResource
from utils.exceptions import InvalidDeviceCodeError
from security_platform.utils.commen import blank_get


# noinspection PyUnresolvedReferences
class AnalysisDataMixin:
    """分析资源混入类"""

    son_label = None

    def get_son_label(self):
        """获取消息解析标签"""
        assert self.son_label is not None, (
                "'%s' should either include a `son_label` attribute, "
                "or override the `get_son_label()` method." % self.__class__.__name__
        )
        return self.son_label

    def _set_device(self):
        """设置关联摄像机"""
        device_code = self.label['device']['device_code']

        try:
            self._device = DeviceInfo.objects.only(
                'device_code',
                'device_name',
                'gis_basic_info',
                'gis_field',
                'cameradevice__flow_address',
                'resource__name',
                'resource__resource_type',
            ).select_related('cameradevice', 'resource').get(device_code=device_code)
        except DeviceInfo.DoesNotExist:
            raise InvalidDeviceCodeError(f'不存在的设备编码:{device_code}')

    @property
    def device(self):
        """获取报警设备"""
        if not hasattr(self, '_device'):
            self._set_device()

        return self._device

    @property
    def camera(self):
        """获取对应资源对象

        1.从摄像机对应关系获取
        2.从报警区域字段获取
        """
        return self.device.cameradevice

    @property
    def resource(self):
        """获取对应资源对象

        1.从摄像机对应关系获取
        2.从报警区域字段获取
        """
        return self.device.resource

    def get_time(self):
        """获取时间"""
        analysis_time = self.label[self.get_son_label()]['time']

        try:
            analysis_time = int(analysis_time)
        except ValueError:
            analysis_time = int(float(analysis_time))

        return datetime.datetime.fromtimestamp(analysis_time)


class GenericAnalysisEventResource(AnalysisDataMixin, CreateLabelResource):
    """视频分析报警事件"""

    priority = 2
    event_name = '视频分析报警'
    model_class = DeviceAlarmEvent
    system_code = EntranceDevice.BelongSystem.ANALYSIS

    def get_create_label(self):
        """创建标签获取"""
        label = OrderedDict()
        label['event_name'] = self.event_name
        label['event_type'] = AlarmEvent.EventType.DEVICE
        label['event_code'] = DeviceAlarmEvent.generate_event_code()
        label['priority'] = self.priority
        label['event_state'] = DeviceAlarmEvent.EventState.UNDISPOSED
        label['alarm_time'] = self.get_time()
        label['subsystem_event_id'] = self.raw_label['msg']['head']['session_id']
        label['alarm_type'] = self.event_name
        label['device'] = self.device
        label['belong_system'] = self.get_system_code().label

        if self.resource is not None:
            label['area_code'] = self.resource.name

        return label

    def relation_create(self, event):
        """关联创建"""
        raise NotImplementedError('method relation_create() must be Implemented.')

    def create(self):
        """模型类数据创建"""
        with transaction.atomic():
            event = super().create()
            relation_instance = self.relation_create(event)

        # 发送事件消息的websocket
        self.publish_obj_ws_message(event, relation_instance)

        return event


class DeployAnalysisEventResource(GenericAnalysisEventResource):
    """布控报警事件"""

    event_name = '布控报警'
    son_label = 'person_monitor'

    def relation_create(self, event):
        """关联数据创建"""
        users_label = self.label[self.son_label]['similars']['users']
        person_info = users_label['personInfo']

        return DeployAlarmRecord.objects.create(
            person_db_image_url=users_label['dbImageUrl'],
            alarm_image_url=self.label[self.son_label]['imgUrl'],
            score=users_label['score'],
            name=blank_get(person_info, 'name'),
            sex=blank_get(person_info, 'sex'),
            born=blank_get(person_info, 'born'),
            type=blank_get(person_info, 'type'),
            number=blank_get(person_info, 'number'),
            country=blank_get(person_info, 'country'),
            city=blank_get(person_info, 'city'),
            db_name=blank_get(person_info, 'db_name'),
            monitor_type=blank_get(person_info, 'monitor_type'),
            db_type=blank_get(person_info, 'db_type'),
            level=blank_get(person_info, 'level'),
            customType=blank_get(person_info, 'customType'),
            event=event,
            resource=self.resource
        )

    # def get_user_info(self, user_id):
    #     """获取用户信息"""
    #     result = requests.get(f'{config_parser.get("API_HOST", "VAS")}/verify/face/gets?imageId={user_id}')
    #     response_data = result.json()
    #
    #     if response_data['result'] != 'success':
    #         raise RequestVASError('获取比对图片失败')
    #
    #     return response_data['data']


class DensityAnalysisEventResource(GenericAnalysisEventResource):
    """密度报警事件"""

    event_name = '密度报警'
    son_label = 'passenger'

    def relation_create(self, event):
        """关联数据创建"""
        return PersonDensityRecord.objects.create(
            total_people_number=self.label[self.son_label]['analyzerResult']['areaNum'],
            alarm_image_url=self.label[self.son_label]['densityImage'],
            event=event,
            resource=self.resource
        )

    def get_create_label(self):
        label = super().get_create_label()
        label['priority'] = self.label[self.son_label]['analyzerResult']['alarmLevel']
        if label['priority'] > 4:
            label['priority'] = 4

        return label


class QueueAnalysisEventResource(GenericAnalysisEventResource):
    """排队报警事件"""

    priority = 3
    event_name = '排队报警'
    son_label = 'passenger'

    def relation_create(self, event):
        pass


class InvasionAnalysisEventResource(GenericAnalysisEventResource):
    """区域入侵报警事件"""

    priority = 2
    event_name = '区域入侵报警'
    son_label = 'behavior'

    def get_time(self):
        """获取时间"""
        return datetime.datetime.fromtimestamp(self.label[self.son_label]['analyzerResult']['time'])

    def relation_create(self, event):
        """关联数据创建"""
        return BehaviorAlarmRecord.objects.create(
            alarm_image_url=self.label[self.son_label]['analyzerResult']['url'],
            event=event,
            resource=self.resource
        )


class BorderAnalysisEventResource(InvasionAnalysisEventResource):
    """越界报警事件"""

    event_name = '越界报警'


class WanderAnalysisEventResource(InvasionAnalysisEventResource):
    """徘徊报警事件"""

    event_name = '徘徊报警'


class RemnantAnalysisEventResource(InvasionAnalysisEventResource):
    """遗留物报警事件"""

    priority = 3
    event_name = '遗留物报警'


class PostureAnalysisEventResource(InvasionAnalysisEventResource):
    """姿态报警事件"""

    priority = 3

    def relation_create(self, event):
        """关联数据创建"""
        return PostureAlarmRecord.objects.create(
            alarm_image_url=self.label[self.son_label]['analyzerResult']['url'],
            action_type=self.label[self.son_label]['analyzerResult']['motionType'],
            event=event,
            resource=self.resource
        )

    def get_create_label(self):
        label = super().get_create_label()
        posture_name = dict(PostureAlarmRecord.PostureType.choices)[
            self.label[self.son_label]['analyzerResult']['motionType']
        ]

        label['event_name'] = f'{posture_name}报警'
        label['alarm_type'] = '姿态动作报警'

        return label


class PlaceAnalysisEventResource(GenericAnalysisEventResource):
    """机位报警事件"""

    priority = 2
    event_name = '机位报警'
    son_label = 'placement'

    def relation_create(self, event):
        """关联数据创建"""
        return PlaceAlarmRecord.objects.create(
            alarm_image_url=self.label[self.son_label]['analyzerResult']['url'],
            event=event,
            resource=self.resource
        )
