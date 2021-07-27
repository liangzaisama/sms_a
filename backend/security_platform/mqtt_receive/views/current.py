"""视频分析实时消息处理

实时消息包括: 排队、人数统计、布控抓拍、机位保障、道口车辆、门禁刷卡
"""
from collections import OrderedDict

from django.db.models import F

from operations.models import EntranceAccessRecords
from security_platform.utils.commen import blank_get
from situations.models import PassageWayCarPassThrough, FlightInfo
from events.models import DeployPersonSnapRecord, PeopleCountingRecord, CameraLineUpRecord, PlaceSafeguardRecord

from utils.exceptions import NoProcessingError
from views.analysis import AnalysisDataMixin
from core.generics import (
    CreateLabelResource, SyncLabelResource, time_format_conversion
)


class LineupCurrentAnalysisResource(AnalysisDataMixin, SyncLabelResource):
    """排队实时"""

    son_label = 'passenger'
    model_class = CameraLineUpRecord

    def get_object_label(self):
        """获取模型类对象参数"""
        return {'camera': self.device}

    def get_sync_label(self):
        """获取标签同步参数"""
        return {
            'current_queue_number': self.label[self.son_label]['analyzerResult']['areaNum'],
            'detection_time': self.get_time(),
            'camera': self.device
        }

    def synchronization(self):
        """模型类资源同步"""
        instance, _ = super().synchronization()
        self.publish_obj_ws_message(instance)

        return instance


class PeopleCountingAnalysisResource(AnalysisDataMixin, SyncLabelResource):
    """人数统计实时"""

    son_label = 'passenger'
    model_class = PeopleCountingRecord

    def get_sync_label(self):
        """配置参数"""
        self.label[self.son_label]['time'] = self.label[self.son_label]['result']['time']

        if not self.label[self.son_label]['result']['data']['upgoing']:
            raise NoProcessingError('非上行方向人员，不处理')

        label = OrderedDict()
        label['camera'] = self.device
        label['statistical_time'] = PeopleCountingRecord.time_to_statistical_time(self.get_time())

        return label

    def synchronization(self):
        """人数同步"""
        label = self.get_sync_label()

        try:
            obj = self.model_class.objects.only('id').get(**label)

            obj.total_people = F('total_people') + 1
            obj.save(update_fields=['total_people'])
        except self.model_class.DoesNotExist:
            obj = self.model_class(**label)
            obj.save()

        return obj


class WebsocketCreateLabelResource(CreateLabelResource):
    """创建成功后发送websocket消息"""

    def create(self):
        """创建资源并发送ws消息"""
        instance = super().create()
        self.publish_obj_ws_message(instance)

        return instance


class DeploySnapAnalysisResource(AnalysisDataMixin, WebsocketCreateLabelResource):
    """布控抓拍"""

    son_label = 'person_monitor'
    model_class = DeployPersonSnapRecord

    def get_create_label(self):
        """获取创建资源的数据"""
        label = OrderedDict()
        # label['resource'] = self.resource
        label['camera'] = self.device
        label['snap_time'] = self.get_time()

        label['snap_image_url'] = self.label[self.son_label]['imgUrl']

        return label


class PlaceSafeguardResource(AnalysisDataMixin, WebsocketCreateLabelResource):
    """机位保障"""

    son_label = 'apron'
    model_class = PlaceSafeguardRecord

    # state_enum: 保障节点枚举值
    # key: 消息保障枚举
    # value: (保障节点描述，二所消息枚举值(存在多个枚举值时第一位进港，第二位离港))
    state_enum = {
        '0': ('飞机离位', '21080'),
        '1': ('飞机入位', '21081'),
        '2': ('客舱门开', '21003'),
        '3': ('客舱门关', '21045'),
        '4': ('货舱门开', '21006'),
        '5': ('货舱门关', '21044'),
        '6': ('轮档上', '21001'),
        '7': ('轮档下', '21073'),
        '10': ('摆渡车到位', '10022,20036'),
        '11': ('摆渡车离位', '20085,20037'),
        '12': ('加油车到位', '21023'),
        '13': ('加油车离位', '21024'),
        '14': ('履带车到位', '20088'),
        '15': ('履带车离位', '20131'),
        '16': ('牵引车到位', '20048'),
        '17': ('牵引车离位', '20052'),
        '18': ('行李车到位', '20185'),
        '19': ('行李车离位', '20186'),
        '20': ('反光背心', '21082'),
    }

    def get_esb_safeguard_code(self, flight):
        """获取保障节点编码"""
        safeguard_desc, safeguard_code = self.state_enum[self.label[self.son_label]['result']['state']]

        if '摆渡车' in safeguard_desc:
            arrival_code, depart_code = safeguard_code.split(',')
            if flight and flight.arrival_departure_flag == FlightInfo.FlightFlag.DEPARTURE:
                # 出港
                return depart_code

            # 进港
            return arrival_code

        return safeguard_code

    def get_create_label(self):
        """获取创建模型类数据"""
        self.label[self.son_label]['time'] = self.label[self.son_label]['result']['time']

        label = OrderedDict()
        label['camera'] = self.device
        label['safeguard_time'] = self.get_time()
        label['safeguard_name'] = self.state_enum[self.label[self.son_label]['result']['state']][0]
        label['safeguard_image_url'] = self.label[self.son_label]['result']['url']
        # print(self.label[self.son_label]['result']['state'])
        # print(label['safeguard_name'])

        if self.resource:
            # 存在对应机位
            queryset = self.resource.flightresource_set.filter(is_using=True).order_by(
                '-actual_start_time', '-plan_start_time')

            if queryset:
                label['flight'] = queryset[0].flight

        return label


class CrossingTrafficResource(WebsocketCreateLabelResource):
    """道口车辆出入信息"""

    model_class = PassageWayCarPassThrough

    def get_create_label(self):
        """获取创建模型类数据"""
        label = OrderedDict()
        label['passageway_name'] = self.label['crossing_name']
        label['passageway_device_code'] = self.label['device_code']
        label['passage_time'] = time_format_conversion(self.label['record_time'])
        label['car_number'] = self.label['car_number']
        label['direction'] = self.label['car_direction']
        label['car_number_image_url'] = self.label['picture_paths'][0]
        label['car_positive_image_url'] = self.label['picture_paths'][1]
        label['car_bottom_image_url'] = self.label['picture_paths'][2]
        label['car_bottom_image_url'] = self.label['picture_paths'][2]
        label['is_allowed'] = self.label['pass_status'] != '3'

        return label


class EntranceSlotCardResource(WebsocketCreateLabelResource):
    """门禁设备刷卡记录"""

    model_class = EntranceAccessRecords

    def get_create_label(self):
        """设置标签值"""
        self.validate_enum_filed('in_out', EntranceAccessRecords.InOutChoice.values)

        label = OrderedDict()
        label['entrance_punch_code'] = self.label['entrance_punch_code']
        label['device_code'] = self.label['device_code']
        label['record_time'] = time_format_conversion(self.label['record_time'])
        label['card_no'] = self.label['card_no']
        label['holder'] = self.label['holder']
        label['department'] = blank_get(self.label, 'department')
        label['code_name'] = blank_get(self.label, 'code_name')
        label['jobs'] = blank_get(self.label, 'jobs')
        label['in_out'] = self.label['in_out']
        label['region_id'] = self.label['region_id']

        return label
