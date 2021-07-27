"""设备相关消息处理

包含各个子系统的：设备新增、设备修改、设备删除、设备状态变更、设备整表同步消息

GenericDeviceResource 通用的设备新增，设备删除，设备修改，设备状态变更业务处理
各系统子类可重写对应的函数来重写或修改业务逻辑
"""
import json
import datetime
from collections import OrderedDict

from security_platform import receive_logger as logger
from security_platform.utils.commen import blank_get
from situations.models import ResourceInfo
from configurations.models import GisPoint
from devices.models import (
    DeviceInfo, CameraDevice, MaintenanceDevice, EntranceDevice, FireDevice, ConcealAlarmDevice,
    PassageWayDevice, WorkSheet
)

from utils.exceptions import NoProcessingError, InvalidMsgFiledError
from core.generics import SwiftCommonLabelResource, time_format_conversion


class GenericDeviceResource(SwiftCommonLabelResource):
    """设备消息处理

    Class Attributes:
        model_class: 设备对应的模型类对象，用于数据库对象操作
        device_type: 设备所属设备类型，根据设备类型的枚举类定义，用于获取设备类型字段
        system_code: 设备所属系统编码，根据系统编码的枚举类定义，用于获取设备系统类型字段
    """

    model_class = DeviceInfo
    device_type = None
    error_message_map = {
        'Not Responding': '设备掉线',
        'Disabled': '设备禁用',
        'Server Not Responding': '设备掉线',
    }

    def get_device_type(self):
        """获取设备类型"""
        assert self.device_type is not None, (
            "'%s' should either include a `device_type` attribute, "
            "or override the `get_device_type()` method." % self.__class__.__name__)
        return self.device_type

    def get_device_state(self, new_device_state):
        """根据当前设备状态及工单状态响应对应的状态"""
        try:
            device = self.get_object()
        except InvalidMsgFiledError:
            # 新增设备 ->new_device_state
            return new_device_state

        if new_device_state == DeviceInfo.DeviceState.TROUBLE_OPEN:
            # 新状态故障 ->故障
            return new_device_state

        # 新状态正常
        if device.device_state == DeviceInfo.DeviceState.NORMAL:
            # 原状态正常 正常->正常
            return new_device_state

        # 原状态故障恢复、故障
        if device.worksheet_set.exclude(sheet_state=WorkSheet.SheetState.CLOSED).exists():
            # 存在工单执行中，故障/故障恢复->故障恢复
            return DeviceInfo.DeviceState.TROUBLE_OFF

        # 没有执行中的工单 故障/故障恢复->正常
        return new_device_state

    def get_error_message(self):
        """获取故障描述"""
        error_message = self.label.get('error_message', '设备故障')
        error_message = self.error_message_map.get(error_message, error_message)

        return error_message

    def get_state_label(self):
        """设备状态变更，数据标签设置"""
        self.validate_enum_filed(
            'device_state',
            [DeviceInfo.DeviceState.NORMAL, DeviceInfo.DeviceState.TROUBLE_OPEN],
            integer=False
        )

        label = OrderedDict()
        label['device_state'] = self.get_device_state(self.label['device_state'])

        if self.label['device_state'] == DeviceInfo.DeviceState.TROUBLE_OPEN:
            # 设备故障
            label['trouble_code'] = self.label.get('error_code', '0')
            label['trouble_time'] = datetime.datetime.now()
            label['trouble_message'] = self.get_error_message()

        return label

    def get_parent(self):
        """找设备的父级设备"""
        try:
            return DeviceInfo.objects.get(device_code=self.label.get('parent_device_code'))
        except DeviceInfo.DoesNotExist:
            # 没找到父设备
            return None

    def get_create_or_update_label(self):
        """获取模型类更新/创建/同步数据"""
        label = self.get_state_label()
        label['device_name'] = self.label['device_name']
        label['device_code'] = self.label['device_code']
        label['parent'] = self.get_parent()
        label['device_type_id'] = blank_get(self.label, 'device_type_id')
        label['device_type_name'] = blank_get(self.label, 'device_type_name')
        label['ipv4'] = blank_get(self.label, 'ip')
        label['port'] = blank_get(self.label, 'port')
        label['switches'] = blank_get(self.label, 'switches')
        label['area_code'] = blank_get(self.label, 'area_code')
        label['floor_code'] = blank_get(self.label, 'floor_code')
        label['manufacturer'] = blank_get(self.label, 'manufacturer_code')
        label['device_model'] = blank_get(self.label, 'device_model')
        label['related_camera_code'] = blank_get(self.label, 'related_camera_code')
        label['device_type_id_son'] = blank_get(self.label, 'device_type_id_son')
        label['device_cad_code'] = blank_get(self.label, 'device_cad_code')
        label['device_type'] = self.get_device_type()
        label['belong_system'] = self.get_system_code()

        return label

    def update(self, *args, **kwargs):
        """发送设备状态的websocket消息"""
        instance = super().update(*args, **kwargs)
        self.publish_obj_ws_message(instance)

        return instance

    def synchronization(self):
        """模型类数据同步

        新增的情况下会推送ws消息
        """
        instance, created = super().synchronization()
        if not created:
            self.publish_obj_ws_message(instance)

        return instance, created

    def get_object_label(self):
        """获取模型类对象查询条件"""
        return {'device_code': self.label['device_code']}


class CameraDeviceResource(GenericDeviceResource):
    """摄像机设备事件"""

    model_class = CameraDevice
    device_type = model_class.DeviceType.CAMERA
    system_code = model_class.BelongSystem.CAMERA

    def validate_device_type(self):
        """排除非摄像机类型的设备"""
        if self.label['device_type_name'] != 'Camera':
            raise NoProcessingError(f"不处理的设备类型:{self.label['device_type_name']}")

    def is_config_camera_info(self, camera_split_list):
        """是否配置摄像机点位信息"""
        if len(camera_split_list) != 3:
            return False

        if camera_split_list[1] not in ['枪机', '球机', '全景', '分析枪机']:
            return False

        return True

    def get_create_or_update_label(self):
        """默认的数据标签设置

        设备新增和设备更新时添加额外字段
        """
        self.validate_device_type()

        label = super().get_create_or_update_label()
        label['is_ptz'] = self.label['ptz'] == 'Yes'
        label['flow_address'] = self.label['rtsp']
        print(self.label['rtsp'])
        # self.label['description'] = '视频分析;1-8#-F1-JX003'

        # 获取设备cad点位信息
        try:
            gis_point = GisPoint.objects.get(dev_guid=label['device_code'])
        except GisPoint.DoesNotExist:
            logger.info(f'{label["device_code"]}未找到gis点位信息')
        else:
            label['device_cad_code'] = gis_point.cad_name
            label['gis_field'] = json.dumps({'MapID': gis_point.map_id, 'LayerID': gis_point.layer_id})
            label['gis_basic_info'] = f'{gis_point.x}, {gis_point.y}'

        # description = self.label.get('description')
        # if description:
        #     split_description = description.split(';')
        #     for desc in split_description:
        #         if '-' in desc:
        #             # 摄像机点位信息
        #             label['device_cad_code'] = desc
        #             break

        # 设备格式示例：C6-18-2 枪机 192.168.21.185
        camera_split_list = self.label['device_name'].split(' ')
        if self.is_config_camera_info(camera_split_list):
            # 设备点位信息分割
            label['area_code'] = camera_split_list[0]
            label['camera_type'] = camera_split_list[1]

            try:
                resource = ResourceInfo.objects.get(name=f'{label["area_code"].split("-")[0]}防区')
            except ResourceInfo.DoesNotExist:
                logger.error(f'未找到对应的围界区域:{label["area_code"]}')
            else:
                label['resource'] = resource

        return label


class MaintenanceDeviceResource(GenericDeviceResource):
    """围界设备事件处理"""

    model_class = MaintenanceDevice
    device_type = model_class.DeviceType.MAINTENANCE
    system_code = model_class.BelongSystem.MAINTENANCE


class PassageWayDeviceResource(GenericDeviceResource):
    """道口设备事件处理"""

    model_class = PassageWayDevice
    device_type = model_class.DeviceType.PASSAGE
    system_code = model_class.BelongSystem.PASSAGE

    def get_create_or_update_label(self):
        label = super().get_create_or_update_label()
        label['area_code'] = f"{self.label['device_code'][0]}号道口"

        return label


class EntranceDeviceResource(GenericDeviceResource):
    """门禁设备事件处理"""

    model_class = EntranceDevice
    device_type = model_class.DeviceType.ENTRANCE
    system_code = model_class.BelongSystem.ENTRANCE

    def get_update_door_status(self):
        """门禁设备门开关事件信息"""
        label = OrderedDict()
        label['open_or_close_time'] = time_format_conversion(self.label['open_or_close_time'])
        label['door_status'] = self.label['door_status']

        return label


class FireDeviceResource(GenericDeviceResource):
    """消防设备事件处理"""

    model_class = FireDevice
    device_type = model_class.DeviceType.FIRE
    system_code = model_class.BelongSystem.FIRE


class ConcealDeviceResource(GenericDeviceResource):
    """隐蔽报警设备事件处理"""

    model_class = ConcealAlarmDevice
    device_type = model_class.DeviceType.CONCEAL
    system_code = model_class.BelongSystem.CONCEAL
