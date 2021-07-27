"""航班关联资源事件

关联资源包括：登机门、值机柜台、转盘、机位
事件包括：新增、删除、修改、同步
"""
from collections import OrderedDict

from security_platform.utils.commen import blank_get
from situations.models import ResourceInfo, FlightCompany, FlightException, Airport

from core.generics import SwiftCommonLabelResource


class GenericIISBasicResource(SwiftCommonLabelResource):
    """航班系统基础资源消息"""

    model_class = ResourceInfo
    resource_type = None

    def get_resource_type(self):
        """获取资源类型"""
        assert self.resource_type is not None, (
                "'%s' should either include a `resource_type` attribute, "
                "or override the `get_resource_type()` method." % self.__class__.__name__
        )
        return self.resource_type

    def get_flight_sys_id(self):
        """获取资源id"""
        return self.label['ID']

    def get_create_or_update_label(self):
        """新增或更新资源"""
        label = OrderedDict()
        label['flight_sys_id'] = self.get_flight_sys_id()
        label['flight_sys_number'] = self.label['CODE']
        label['chinese_desc'] = blank_get(self.label, 'CNNM')
        label['english_desc'] = blank_get(self.label, 'ENNM')
        label['nature'] = blank_get(self.label, 'ATTR')
        label['flight_sys_statue'] = self.label['STUS']
        label['terminal_number'] = blank_get(self.label, 'TMLC')
        label['name'] = self.label['CNNM'] or self.label['CODE']
        label['resource_type'] = self.get_resource_type()
        label['exit_number'] = blank_get(self.label, 'EXNO')

        return label

    def get_object_label(self):
        """获取资源id"""
        return {'flight_sys_id': self.label['ID']}


class BoardingResource(GenericIISBasicResource):
    """登机口"""

    resource_type = ResourceInfo.ResourceType.BOARDING


class BaggageResource(GenericIISBasicResource):
    """转盘"""

    resource_type = ResourceInfo.ResourceType.BAGGAGE


class CounterResource(GenericIISBasicResource):
    """值机柜台"""

    resource_type = ResourceInfo.ResourceType.COUNTER


class PlacementResource(GenericIISBasicResource):
    """机位"""

    resource_type = ResourceInfo.ResourceType.PLACEMENT

    def get_flight_sys_id(self):
        return self.label['CODE']

    def get_object_label(self):
        return {'flight_sys_id': self.label['CODE']}


class AirlinesLabelResource(SwiftCommonLabelResource):
    """航空公司事件处理

    Class Attributes:
        model_class: 航空公司数据模型类
    """

    model_class = FlightCompany

    def get_create_or_update_label(self):
        """航空公司数据标签，不存在的字典用None来表示"""
        label = OrderedDict()
        label['second_code'] = self.label['CODE']
        label['three_code'] = self.label.get('TRCD')
        label['property'] = self.label.get('ALTA')
        label['ch_description'] = self.label.get('CNNM')
        label['inter_description'] = self.label.get('ENNM')
        label['country_code'] = self.label.get('CTRY')
        label['terminal'] = self.label.get('TMLC')
        label['company_group'] = self.label.get('GRUP')

        return label

    def get_object_label(self):
        """查询航空公司过滤数据字典"""
        return {'second_code': self.label['CODE']}


class FlightErrorLabelResource(SwiftCommonLabelResource):
    """航班异常原因"""

    model_class = FlightException

    def get_create_or_update_label(self):
        """航班异常原因数据标签，不存在的字典用None来表示"""
        label = OrderedDict()
        label['errcode'] = self.label['CODE']
        label['ch_description'] = self.label.get('CNNM')
        label['inter_description'] = self.label.get('ENNM')
        label['errcode_belong'] = self.label.get('SPCD')
        label['is_type'] = self.label.get('ISSP')
        label['errcode_type'] = self.label.get('ARTY')

        return label

    def get_object_label(self):
        """查询航班异常原因过滤数据字典"""
        return {'errcode': self.label['CODE']}


class AirportLabelResource(SwiftCommonLabelResource):
    """机场信息"""

    model_class = Airport

    def get_create_or_update_label(self):
        """机场信息数据标签，不存在的字典用None来表示"""
        label = OrderedDict()
        label['three_code'] = self.label['CODE']
        label['four_code'] = self.label.get('FRCD')
        label['property'] = self.label.get('APAT')
        label['ch_description'] = self.label.get('CNNM')
        label['inter_description'] = self.label.get('ENNM')
        label['is_open'] = self.label.get('AISO')
        label['alias'] = self.label.get('APSN')
        label['country_code'] = self.label.get('CTRY')
        label['city_code'] = self.label.get('ACTY')
        label['lat'] = self.label.get('LAT')
        label['lon'] = self.label.get('LON')

        return label

    def get_object_label(self):
        """查询机场信息过滤数据字典"""
        return {'three_code': self.label['CODE']}
