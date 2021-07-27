"""子系统的报警相关消息业务逻辑处理

GenericEventResource 通用的触发报警，确认报警，处置报警
各系统子类可重写对应的函数来重写或修改业务逻辑
"""
from collections import OrderedDict

from django.db import transaction
from django.db.models import ObjectDoesNotExist

from security_platform.utils.commen import blank_get
from devices import models
from events.serializers import MonitorScopesAlarmSerializer
from events.models import AlarmEvent, DeviceAlarmEvent, DeviceAlarmEventCamera, DeviceAlarmEventPicture

from utils.exceptions import InvalidDeviceCodeError
from core.generics import CreateUpdateLabelResource, time_format_conversion, publish_ws_message


class GenericEventResource(CreateUpdateLabelResource):
    """通用报警事件处理

    Class Attributes:
        model_class: 设备对应的模型类对象，用于数据库对象操作
    """

    model_class = DeviceAlarmEvent

    def create_event_camera(self, event):
        """报警事件关联摄像机生成器"""
        for camera_data in self.label.get('camer_list', []):
            yield DeviceAlarmEventCamera(
                event=event,
                code=camera_data['camer_guid'],
                preset=camera_data['camer_persetid']
            )

    def create_event_picture(self, event):
        """报警事件关联图片生成器"""
        for picture_addr in self.label.get('picture_paths', []):
            yield DeviceAlarmEventPicture(event=event, address=picture_addr)

    def create(self):
        """创建事件及关联数据

        创建数据包括：报警事件数据，报警事件关联摄像机数据，报警事件关联图片数据

        Returns:
            event：事件模型类对象
        """
        with transaction.atomic():
            event = super().create()

            DeviceAlarmEventCamera.objects.bulk_create(list(self.create_event_camera(event)))
            DeviceAlarmEventPicture.objects.bulk_create(list(self.create_event_picture(event)))

        # 发送事件消息的websocket
        self.publish_obj_ws_message(event)

        return event

    def device_validate(self):
        """设备校验"""
        try:
            device = models.DeviceInfo.objects.select_related('resource').get(device_code=self.label['device_code'])
        except ObjectDoesNotExist:
            raise InvalidDeviceCodeError(f'不存在的设备编码:{self.label["device_code"]}')

        return device

    def device_list_validate(self):
        """设备校验"""
        device = None
        for camera_data in self.label['camer_list']:
            try:
                device = models.DeviceInfo.objects.select_related('resource').get(device_code=camera_data['camer_guid'])
            except ObjectDoesNotExist:
                continue
            else:
                break

        if device is None:
            raise InvalidDeviceCodeError(f'camer_list中的设备编码不存在')

        return device

    def get_create_label(self):
        """触发报警事件"""
        label = OrderedDict()
        label['event_name'] = self.label['event_name']
        label['event_code'] = DeviceAlarmEvent.generate_event_code()
        label['alarm_time'] = time_format_conversion(self.label['event_time'])
        label['area_code'] = blank_get(self.label, 'area_code')
        label['floor_code'] = blank_get(self.label, 'floor_code')
        label['priority'] = self.label['priority']
        label['event_state'] = DeviceAlarmEvent.EventState.UNDISPOSED
        label['event_description'] = self.label['event_message']
        label['subsystem_event_id'] = self.label['event_code']
        label['alarm_type'] = self.label['event_type']
        label['event_type'] = AlarmEvent.EventType.DEVICE
        label['belong_system'] = self.system_code.label

        if label['event_name'] == '隐蔽事件':
            device = self.device_list_validate()
        else:
            device = self.device_validate()

        label['device'] = device
        label['area_code'] = getattr(device.resource, 'name', '')

        # 事件报警图片暂时未获取，因界面无地方展示，后续如果需要展示需要添加，
        # 获取需要调用webapi获取事件的报警图片

        return label

    def get_update_label(self):
        """事件处置"""
        label = OrderedDict()
        label['subsystem_event_id'] = self.label['event_code']
        label['dispose_time'] = time_format_conversion(self.label['deactive_time'])
        label['dispose_opinion'] = self.label['deactive_message']
        label['dispose_user'] = self.label.get('deactive_user', self.system_code.label)
        label['event_state'] = DeviceAlarmEvent.EventState.RELIEVED

        return label

    def get_object_label(self):
        """查询报警事件数据时的过滤条件"""
        return {
            'subsystem_event_id': self.label['event_code'],
            'event_state': DeviceAlarmEvent.EventState.UNDISPOSED
        }


class CameraEventResource(GenericEventResource):
    """视频监控平台报警事件"""

    system_code = models.EntranceDevice.BelongSystem.CAMERA

    def create(self):
        event = super().create()
        if event.event_name == '围界报警':
            # 发送围界socket消息
            publish_ws_message('scopes_event', MonitorScopesAlarmSerializer(instance=event).data)

        return event


class MaintenanceEventResource(GenericEventResource):
    """围界报警事件"""

    system_code = models.EntranceDevice.BelongSystem.MAINTENANCE


class EntranceEventResource(GenericEventResource):
    """门禁报警事件"""

    system_code = models.EntranceDevice.BelongSystem.ENTRANCE

    def get_create_label(self):
        label = super().get_create_label()
        label['pass_id'] = blank_get(self.label, 'passcard_id')

        return label


class FireEventResource(GenericEventResource):
    """消防报警事件"""

    system_code = models.EntranceDevice.BelongSystem.FIRE


class ConcealEventResource(GenericEventResource):
    """隐蔽报警事件"""

    system_code = models.EntranceDevice.BelongSystem.CONCEAL


class PassageWayEventResource(GenericEventResource):
    """道口报警事件"""

    system_code = models.EntranceDevice.BelongSystem.PASSAGE

    def get_create_label(self):
        label = super().get_create_label()
        label['area_code'] = blank_get(self.label, 'area_code')

        return label
