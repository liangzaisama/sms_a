"""航班事件处理

包括：航班新增、航班变更、航班删除、航班表同步
"""
from collections import OrderedDict

from django.db import transaction

from security_platform.utils.commen import datetime_to_str
from situations.models import ResourceInfo, FlightInfo, FlightResource

from utils.exceptions import InvalidMsgFiledError
from core.generics import SwiftCommonLabelResource, time_format_conversion, LabelResourceBulkProxy, publish_ws_message


class FlightRelatedResource(SwiftCommonLabelResource):
    """关联航班资源更新

    登机门、转盘
    """

    resource_key_name = 'ID'
    model_class = FlightResource

    def __init__(self, *args, **kwargs):
        self._related_resource = None
        super().__init__(*args, **kwargs)

    def _set_related_resource(self):
        try:
            self._related_resource = ResourceInfo.objects.get(flight_sys_id=self.label[self.resource_key_name])
        except ResourceInfo.DoesNotExist:
            raise InvalidMsgFiledError(f'错误的航班系统资源ID:{self.label[self.resource_key_name]}')

    @property
    def related_resource(self):
        """获取关联资源"""
        if self._related_resource is None:
            self._set_related_resource()

        return self._related_resource

    def get_object_label(self):
        """获取航班过滤数据"""
        return {'flight_id': self.label['flight_id'], 'resource': self.related_resource}

    def get_create_or_update_label(self):
        """更新或新增关联航班资源"""
        label = OrderedDict()
        label['resource'] = self.related_resource
        label['flight_id'] = self.label['flight_id']
        label['plan_start_time'] = time_format_conversion(self.label['ESTR'])
        label['plan_end_time'] = time_format_conversion(self.label['EEND'])
        label['actual_start_time'] = time_format_conversion(self.label['RSTR'])
        label['actual_end_time'] = time_format_conversion(self.label['REND'])

        return label


class FlightPlacementResource(FlightRelatedResource):
    """机位更新"""

    resource_key_name = 'CODE'

    def get_create_or_update_label(self):
        label = super().get_create_or_update_label()
        label['is_using'] = self.label.get('CSSI') == 'Y'

        ws_message = label.copy()
        resource = ws_message.pop('resource')
        ws_message['resource_id'] = resource.id
        ws_message['resource_name'] = resource.name
        ws_message['resource_type'] = resource.resource_type
        ws_message['flight_number'] = self.label['flight_number']
        ws_message['plan_start_time'] = datetime_to_str(label['plan_start_time'])
        ws_message['plan_end_time'] = datetime_to_str(label['plan_end_time'])
        ws_message['actual_start_time'] = datetime_to_str(label['actual_start_time'])
        ws_message['actual_end_time'] = datetime_to_str(label['actual_end_time'])

        publish_ws_message('placement', ws_message)

        return label


class FlightLabelResource(SwiftCommonLabelResource):
    """航班事件处理"""

    model_class = FlightInfo

    def get_create_or_update_label(self):
        """航班新增或更新"""
        flight_label = OrderedDict()
        self.get_flight_basic(flight_label)
        self.get_flight_routes(flight_label)

        return flight_label

    def get_object_label(self):
        """获取航班"""
        return {'fl_id': self.label['FLID']}

    def get_create_label(self):
        """航班新增"""
        return self.get_create_or_update_label()

    def get_sync_label(self):
        """航班同步"""
        return self.get_create_or_update_label()

    def remove_null_fields(self, data):
        """移除null字段"""
        copy_data = data.copy()
        for key, value in data.items():
            if value is None:
                copy_data.pop(key)

        return copy_data

    def get_update_label(self):
        """航班信息更新"""
        label = OrderedDict()

        if self.label.get('AIRL') is not None:
            self.get_flight_routes(label)
        else:
            # 航班计划时间更新
            label['plan_takeoff'] = time_format_conversion(self.label.get('FPTT'))
            label['plan_arrival'] = time_format_conversion(self.label.get('FPLT'))
            label['estimate_takeoff'] = time_format_conversion(self.label.get('FETT'))
            label['estimate_arrival'] = time_format_conversion(self.label.get('FELT'))
            label['actual_takeoff'] = time_format_conversion(self.label.get('FRTT'))
            label['actual_arrive'] = time_format_conversion(self.label.get('FRLT'))

        if self.label.get('TMCD') is not None:
            # 航站楼更新
            label['terminal_info'] = self.label['TMCD'].get('NMCD')
            label['inter_terminal_info'] = self.label['TMCD'].get('JMCD')

        # 航班基础信息更新
        label['flight_number'] = self.label.get('NFLN')
        label['company'] = self.label.get('NAWC')
        label['flight_state'] = self.label.get('STAT')
        label['start_boarding_time'] = time_format_conversion(self.label.get('BORT'))
        label['end_boarding_time'] = time_format_conversion(self.label.get('POKT'))
        label['exception_status'] = self.label.get('ABST')
        label['exception_reason_father'] = self.label.get('ABRS')
        label['exception_reason_son'] = self.label.get('IARS')
        label['flight_property'] = self.label.get('FATT')

        return self.remove_null_fields(label)

    def get_flight_basic(self, label):
        """获取航班基础信息"""
        label['fl_id'] = self.label['FLID']
        label['ff_id'] = self.label['FFID']
        label['mf_id'] = self.label['MFID']
        label['mf_fi'] = self.label['MFFI']
        label['fl_tk'] = self.label['FLTK']
        label['flight_number'] = self.label['AWCD'] + self.label['FLNO']
        label['company'] = self.label['AWCD']
        label['execution_date'] = time_format_conversion(self.label['FEXD'], format='%Y%m%d')
        label['arrival_departure_flag'] = self.label['FLIO']
        label['flight_property'] = self.label['FATT']
        label['flight_state'] = self.label['STAT']
        label['exception_status'] = self.label['ABST']
        label['exception_reason_father'] = self.label['ABRS']
        label['exception_reason_son'] = self.label['IARS']
        label['start_boarding_time'] = time_format_conversion(self.label.get('BORT'))
        label['end_boarding_time'] = time_format_conversion(self.label.get('POKT'))
        label['terminal_info'] = self.label['TMCD'].get('NMCD')
        label['inter_terminal_info'] = self.label['TMCD'].get('JMCD')

    def get_flight_routes(self, label):
        """获取航线信息"""
        flight_routes_label = self.label['AIRL']
        terminal_label = flight_routes_label['ARPT']
        label['takeoff_iata'] = terminal_label[0]['APCD']
        label['destination_iata'] = terminal_label[-1]['APCD']
        label['stopover_iata'] = ','.join(i['APCD'] for i in terminal_label[1:-1])
        label['plan_takeoff'] = time_format_conversion(terminal_label[0]['FPTT'])
        label['estimate_takeoff'] = time_format_conversion(terminal_label[0]['FETT'])
        label['actual_takeoff'] = time_format_conversion(terminal_label[0]['FRTT'])
        label['plan_arrival'] = time_format_conversion(terminal_label[-1]['FPLT'])
        label['estimate_arrival'] = time_format_conversion(terminal_label[-1]['FELT'])
        label['actual_arrive'] = time_format_conversion(terminal_label[-1]['FRLT'])

    def run_related_util(self, father_label, son_label, related_class, context, method):
        """执行关联资源的更新/新增/同步

        Args:
            father_label: 资源父级标签
            son_label: 资源子级标签
            related_class: 关联资源类
            context: 上下文信息
            method: 操作方式
        """
        father_label = self.label.get(father_label)
        if father_label is not None:
            obj = LabelResourceBulkProxy(father_label, son_label, related_class, context=context)
            getattr(obj, method)()

    def _do_related_resource_method(self, flight, method):
        """关联航班对象更新或创建

        GTLS：登机门
        BLLS：转盘
        STLS：机位
        """
        context = {'flight_id': flight.id, 'flight_number': flight.flight_number}
        self.run_related_util('GTLS', ('GATE',), FlightRelatedResource, context, method)
        self.run_related_util('BLLS', ('BELT',), FlightRelatedResource, context, method)
        self.run_related_util('STLS', ('STND',), FlightPlacementResource, context, method)

    def create(self):
        """航班新增"""
        with transaction.atomic():
            flight = super().create()
            self._do_related_resource_method(flight, 'create')

    def synchronization(self):
        """航班同步"""
        with transaction.atomic():
            flight, _ = super().synchronization()
            self._do_related_resource_method(flight, 'synchronization')

    def update(self, *args, **kwargs):
        """航班更新"""
        with transaction.atomic():
            flight = super().update(*args, **kwargs)
            self._do_related_resource_method(flight, 'synchronization')
