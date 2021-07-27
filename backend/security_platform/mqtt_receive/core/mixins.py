"""消息处理的Mixin类，配置装饰器及数据对象进行业务处理。

由消息worker类继承Mixin类，来获取对应的实现消息处理方法。
包含事件内容：
1 各个子系统的设备相关事件
2 各个子系统的报警事件
3 视频分析报警事件
4 航班事件

Example:
    class CommonWork(AbstractWorker,
                 mixins.PassageWayMixin,
                 mixins.CameraMixin):
    pass

需要websocket的消息
设备状态变更
报警触发、报警处置
门禁刷卡
道口车辆出入信息
"""
from collections import OrderedDict

from core.generics import LabelResourceBulkProxy
from decorate.send_iis import SendIIS

from views import event, device, analysis, current, flight, flightresource, staff


class MsgNestedSeq:
    """标签顺序枚举"""

    # 基础标签
    COMMON_NESTED_SEQ = ('msg', 'body')
    # 设备
    DEVICE_NESTED_SEQ = ('msg', 'body', 'device')
    # 设备状态
    DEVICE_STATE_NESTED_SEQ = ('msg', 'body', 'device_status')
    # 设备同步列表
    DEVICE_SYNC_NESTED_SEQ = ('msg', 'body', 'device_sync', 'device_list')
    # 事件
    ALARM_EVENT_NESTED_SEQ = ('msg', 'body', 'event')
    # 道口车辆出入信息
    CROSSING_TRAFFIC_NESTED_SEQ = ('msg', 'body', 'car_transit')
    # 门禁刷卡信息
    ENTRANCE_PUNCH_NESTED_SEQ = ('msg', 'body', 'entrance_punch')
    # 门禁门开关信息
    ENTRANCE_DOOR_NESTED_SEQ = ('msg', 'body', 'entrance_punch')
    # 航班登机口
    BOARDING_NESTED_SEQ = ('MSG', 'GATE')
    # 航班转盘
    BAGGAGE_NESTED_SEQ = ('MSG', 'BELT')
    # 航班值机柜台
    COUNTER_NESTED_SEQ = ('MSG', 'CNTR')
    # 航班机位
    PLACEMENT_NESTED_SEQ = ('MSG', 'STND')
    # 航班信息
    FLIGHT_NESTED_SEQ = ('MSG', 'DFLT')
    # 异常信息
    FLIGHT_EXCEPTION_NESTED_SEQ = ('MSG', 'ABRN')
    # 航空公司
    FLIGHT_COMPANY_NESTED_SEQ = ('MSG', 'AWAY')
    # 机场
    FLIGHT_AIRPORT_NESTED_SEQ = ('MSG', 'APOT')


class MaintenanceMixin:
    """围界事件处理"""

    def ais_alarm_trigger(self, label):
        """围界报警触发"""
        return event.MaintenanceEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).create()

    def ais_alarm_deactive(self, label):
        """围界报警处置"""
        return event.MaintenanceEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).update()

    def ais_device_add(self, label):
        """围界设备新增"""
        return device.MaintenanceDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).create()

    def ais_device_delete(self, label):
        """围界设备删除"""
        return device.MaintenanceDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).delete(fake=True)

    def ais_device_update(self, label):
        """围界设备更新"""
        return device.MaintenanceDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).update()

    def ais_device_statechange(self, label):
        """围界设备状态变更"""
        return device.MaintenanceDeviceResource(label, MsgNestedSeq.DEVICE_STATE_NESTED_SEQ).update(
            label_method='get_state_label')

    def ais_device_sync(self, label):
        """围界设备整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.DEVICE_SYNC_NESTED_SEQ,
                                      device.MaintenanceDeviceResource).synchronization()


class EntranceMixin:
    """门禁事件处理"""

    def acs_alarm_trigger(self, label):
        """门禁报警触发"""
        return event.EntranceEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).create()

    def acs_alarm_deactive(self, label):
        """门禁报警处置"""
        return event.EntranceEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).update()

    def acs_device_add(self, label):
        """门禁设备新增"""
        return device.EntranceDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).create()

    def acs_device_delete(self, label):
        """门禁设备删除"""
        return device.EntranceDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).delete(fake=True)

    def acs_device_update(self, label):
        """门禁设备更新"""
        return device.EntranceDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).update()

    def acs_device_statechange(self, label):
        """门禁设备状态变更"""
        return device.EntranceDeviceResource(label, MsgNestedSeq.DEVICE_STATE_NESTED_SEQ).update(
            label_method='get_state_label')

    def acs_device_sync(self, label):
        """门禁设备整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.DEVICE_SYNC_NESTED_SEQ,
                                      device.EntranceDeviceResource).synchronization()

    def acs_accesscontrol_paybycard(self, label):
        """门禁设备刷卡记录"""
        return current.EntranceSlotCardResource(label, MsgNestedSeq.ENTRANCE_PUNCH_NESTED_SEQ).create()

    def acs_accesscontrol_door(self, label):
        """门禁开关记录"""
        return device.EntranceDeviceResource(label, MsgNestedSeq.ENTRANCE_DOOR_NESTED_SEQ).update(
            label_method='get_update_door_status')


class PassCardMixin:
    """通行证信息"""

    PASS_CARD_INFO_NESTED_SEQ = ('msg', 'body', 'passcard_info')
    PASS_CARD_SYNC_NESTED_SEQ = ('msg', 'body', 'passcard_sync', 'passcard_list')
    label_class = staff.StaffResource

    def acs_perinfomation_add(self, label):
        """通行证新增 卡回收后有可能出现重复数据"""
        return self.label_class(label, self.PASS_CARD_INFO_NESTED_SEQ).synchronization()

    def acs_perinfomation_delete(self, label):
        """通行证删除"""
        return self.label_class(label, self.PASS_CARD_INFO_NESTED_SEQ).delete()

    def acs_perinfomation_update(self, label):
        """通行证更新"""
        return self.label_class(label, self.PASS_CARD_INFO_NESTED_SEQ).update()

    def acs_perinfomation_sync(self, label):
        """通行证同步"""
        return LabelResourceBulkProxy(label, self.PASS_CARD_SYNC_NESTED_SEQ, self.label_class).synchronization()


class FireMixin:
    """消防事件处理"""

    def xfhz_alarm_trigger(self, label):
        """消防报警触发"""
        return event.FireEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).create()

    def xfhz_alarm_deactive(self, label):
        """消防报警处置"""
        return event.FireEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).update()

    def xfhz_device_add(self, label):
        """消防设备新增"""
        return device.FireDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).create()

    def xfhz_device_delete(self, label):
        """消防设备删除"""
        return device.FireDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).delete(fake=True)

    def xfhz_device_update(self, label):
        """消防设备更新"""
        return device.FireDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).update()

    def xfhz_device_statechange(self, label):
        """消防设备状态变更"""
        return device.FireDeviceResource(label, MsgNestedSeq.DEVICE_STATE_NESTED_SEQ).update(
            label_method='get_state_label')

    def xfhz_device_sync(self, label):
        """消防设备整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.DEVICE_SYNC_NESTED_SEQ,
                                      device.FireDeviceResource).synchronization()


class ConcealMixin:
    """隐蔽报警事件处理"""

    def ybbj_alarm_trigger(self, label):
        """隐蔽报警触发"""
        return event.ConcealEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).create()

    def ybbj_alarm_deactive(self, label):
        """隐蔽报警处置"""
        return event.ConcealEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).update()

    def ybbj_device_add(self, label):
        """隐蔽设备新增"""
        return device.ConcealDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).create()

    def ybbj_device_delete(self, label):
        """隐蔽设备删除"""
        return device.ConcealDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).delete(fake=True)

    def ybbj_device_update(self, label):
        """隐蔽设备更新"""
        return device.ConcealDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).update()

    def ybbj_device_statechange(self, label):
        """隐蔽设备状态变更"""
        return device.ConcealDeviceResource(label, MsgNestedSeq.DEVICE_STATE_NESTED_SEQ).update(
            label_method='get_state_label')

    def ybbj_device_sync(self, label):
        """隐蔽设备整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.DEVICE_SYNC_NESTED_SEQ,
                                      device.ConcealDeviceResource).synchronization()


class PassageWayMixin:
    """道口事件处理"""

    def cms_alarm_trigger(self, label):
        """道口报警触发"""
        return event.PassageWayEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).create()

    def cms_alarm_deactive(self, label):
        """道口报警处置"""
        return event.PassageWayEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).update()

    def cms_device_add(self, label):
        """道口设备新增"""
        return device.PassageWayDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).create()

    def cms_device_delete(self, label):
        """道口设备删除"""
        return device.PassageWayDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).delete(fake=True)

    def cms_device_update(self, label):
        """道口设备更新"""
        return device.PassageWayDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).update()

    def cms_device_sync(self, label):
        """道口设备整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.DEVICE_SYNC_NESTED_SEQ,
                                      device.PassageWayDeviceResource).synchronization()

    def cms_device_statechange(self, label):
        """道口设备状态变更"""
        return device.PassageWayDeviceResource(label, MsgNestedSeq.DEVICE_STATE_NESTED_SEQ).update(
            label_method='get_state_label')

    def cms_car_transit(self, label):
        """道口车辆出入记录"""
        return current.CrossingTrafficResource(label, MsgNestedSeq.CROSSING_TRAFFIC_NESTED_SEQ).create()


class CameraMixin:
    """视频监控事件处理"""

    def vms_device_add(self, label):
        """摄像机设备新增"""
        return device.CameraDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).create()

    def vms_device_delete(self, label):
        """摄像机设备删除"""
        return device.CameraDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).delete(fake=True)

    def vms_device_update(self, label):
        """摄像机设备更新"""
        return device.CameraDeviceResource(label, MsgNestedSeq.DEVICE_NESTED_SEQ).update()

    def vms_device_sync(self, label):
        """摄像机整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.DEVICE_SYNC_NESTED_SEQ,
                                      device.CameraDeviceResource).synchronization()

    def vms_device_statechange(self, label):
        """摄像机设备状态变更"""
        return device.CameraDeviceResource(label, MsgNestedSeq.DEVICE_STATE_NESTED_SEQ).update(
            label_method='get_state_label')

    def vms_alarm_trigger(self, label):
        """摄像机报警触发"""
        return event.CameraEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).create()

    def vms_alarm_deactive(self, label):
        """摄像机报警处置"""
        return event.CameraEventResource(label, MsgNestedSeq.ALARM_EVENT_NESTED_SEQ).update()


class VideoAnalysisMixin:
    """视频分析报警消息处理"""

    @SendIIS('SIP', 'REALTIMEALARM')
    def zvams_alarm_trigger(self, label):
        """布控报警"""
        return analysis.DeployAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'REALTIMEDENSITY')
    def zvams_analysis_people_density(self, label):
        """密度实时，不需要处理"""
        pass

    @SendIIS('SIP', 'ALARMDENSITY')
    def zvams_analysis_density_alarm(self, label):
        """密度报警"""
        return analysis.DensityAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'ALARMQUEUE')
    def zvams_analysis_queue_alarm(self, label):
        """排队报警"""
        return analysis.QueueAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'ALARMINVASION')
    def zvams_discern_behavior_areainvasion(self, label):
        """入侵"""
        return analysis.InvasionAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'ALARMBORDER')
    def zvams_discern_behavior_border(self, label):
        """越界"""
        return analysis.BorderAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'ALARMWANDERING')
    def zvams_discern_behavior_wandering(self, label):
        """徘徊"""
        return analysis.WanderAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    def zvams_discern_behavior_carryover(self, label):
        """遗留物"""
        return analysis.RemnantAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    def zvams_discern_behavior_posture(self, label):
        """姿态"""
        return analysis.PostureAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'CAPTURE')
    def zvams_face_capture(self, label):
        """布控抓拍"""
        return current.DeploySnapAnalysisResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('SIP', 'REALTIMEQUEUE')
    def zvams_analysis_people_queue(self, label):
        """排队实时"""
        return current.LineupCurrentAnalysisResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).synchronization()

    @SendIIS('SIP', 'REALTIMECHANNEL')
    def zvams_analysis_people_counting(self, label):
        """人数统计实时"""
        return current.PeopleCountingAnalysisResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).synchronization()

    def zvams_placement_alarm(self, label):
        """机场报警"""
        return analysis.PlaceAnalysisEventResource(label, MsgNestedSeq.COMMON_NESTED_SEQ).create()

    @SendIIS('DFME', 'DPUE')
    def zvams_discern_object_apron(self, label):
        """机位保障信息"""
        place_safeguard_resource = current.PlaceSafeguardResource(label, MsgNestedSeq.COMMON_NESTED_SEQ)
        safeguard_record = place_safeguard_resource.create()
        label.pop('msg')
        label.pop('tag')
        label['DFLT'] = OrderedDict()

        if safeguard_record.flight:
            label['DFLT']['FLID'] = safeguard_record.flight.fl_id
            label['DFLT']['FFID'] = safeguard_record.flight.ff_id
            label['DFLT']['MFID'] = safeguard_record.flight.mf_id
            label['DFLT']['MFFI'] = safeguard_record.flight.mf_fi
            label['DFLT']['FLTK'] = safeguard_record.flight.fl_tk
            label['DFLT']['DILG'] = OrderedDict()
            label['DFLT']['DILG']['CODE'] = place_safeguard_resource.get_esb_safeguard_code(safeguard_record.flight)
            label['DFLT']['DILG']['CDNO'] = 1
            label['DFLT']['DILG']['RSTT'] = str(safeguard_record.safeguard_time)

        print(label)
        return safeguard_record


class ParkMixin:
    """停车场系统"""
    pass


class IISGateResourceMixin:
    """登机门消息处理"""

    def iis_gtie(self, label):
        """登机门新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BOARDING_NESTED_SEQ,
                                      flightresource.BoardingResource).create()

    def iis_gtue(self, label):
        """登机门修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BOARDING_NESTED_SEQ,
                                      flightresource.BoardingResource).update()

    def iis_gtde(self, label):
        """登机门删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BOARDING_NESTED_SEQ,
                                      flightresource.BoardingResource).delete()

    def iis_gtdl(self, label):
        """登机门整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BOARDING_NESTED_SEQ,
                                      flightresource.BoardingResource).synchronization()


class IISBaggageResourceMixin:
    """转盘消息处理"""

    def iis_blie(self, label):
        """转盘新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BAGGAGE_NESTED_SEQ,
                                      flightresource.BaggageResource).create()

    def iis_blue(self, label):
        """转盘修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BAGGAGE_NESTED_SEQ,
                                      flightresource.BaggageResource).update()

    def iis_blde(self, label):
        """转盘删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BAGGAGE_NESTED_SEQ,
                                      flightresource.BaggageResource).delete()

    def iis_bldl(self, label):
        """转盘整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.BAGGAGE_NESTED_SEQ,
                                      flightresource.BaggageResource).synchronization()


class IISCounterResourceMixin:
    """柜台消息处理"""

    def iis_ccie(self, label):
        """值机柜台新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.COUNTER_NESTED_SEQ,
                                      flightresource.CounterResource).create()

    def iis_ccue(self, label):
        """值机柜台修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.COUNTER_NESTED_SEQ,
                                      flightresource.CounterResource).update()

    def iis_ccde(self, label):
        """值机柜台删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.COUNTER_NESTED_SEQ,
                                      flightresource.CounterResource).delete()

    def iis_ccdl(self, label):
        """值机柜台整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.COUNTER_NESTED_SEQ,
                                      flightresource.CounterResource).synchronization()


class IISPlacementResourceMixin:
    """机位消息处理"""

    def iis_stie(self, label):
        """机位新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.PLACEMENT_NESTED_SEQ,
                                      flightresource.PlacementResource).create()

    def iis_stue(self, label):
        """机位修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.PLACEMENT_NESTED_SEQ,
                                      flightresource.PlacementResource).update()

    def iis_stde(self, label):
        """机位删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.PLACEMENT_NESTED_SEQ,
                                      flightresource.PlacementResource).delete()

    def iis_stdl(self, label):
        """机位整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.PLACEMENT_NESTED_SEQ,
                                      flightresource.PlacementResource).synchronization()


class IISExceptionMixin:
    """航班系统异常消息处理"""

    def iis_arie(self, label):
        """航班异常消息新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_EXCEPTION_NESTED_SEQ,
                                      flightresource.FlightErrorLabelResource).create()

    def iis_arue(self, label):
        """航班异常消息修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_EXCEPTION_NESTED_SEQ,
                                      flightresource.FlightErrorLabelResource).update()

    def iis_arde(self, label):
        """航班异常消息删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_EXCEPTION_NESTED_SEQ,
                                      flightresource.FlightErrorLabelResource).delete()

    def iis_ardl(self, label):
        """航班异常整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_EXCEPTION_NESTED_SEQ,
                                      flightresource.FlightErrorLabelResource).synchronization()


class IISCompanyMixin:
    """航班系统航空公司消息处理"""

    def iis_awie(self, label):
        """航空公司新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_COMPANY_NESTED_SEQ,
                                      flightresource.AirlinesLabelResource).create()

    def iis_awue(self, label):
        """航空公司修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_COMPANY_NESTED_SEQ,
                                      flightresource.AirlinesLabelResource).update()

    def iis_awde(self, label):
        """航空公司删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_COMPANY_NESTED_SEQ,
                                      flightresource.AirlinesLabelResource).delete()

    def iis_awdl(self, label):
        """航空公司整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_COMPANY_NESTED_SEQ,
                                      flightresource.AirlinesLabelResource).synchronization()


class IISAirportMixin:
    """航班系统机场消息处理"""

    def iis_apie(self, label):
        """机场新增"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_AIRPORT_NESTED_SEQ,
                                      flightresource.AirportLabelResource).create()

    def iis_apue(self, label):
        """机场修改"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_AIRPORT_NESTED_SEQ,
                                      flightresource.AirportLabelResource).update()

    def iis_apde(self, label):
        """机场删除"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_AIRPORT_NESTED_SEQ,
                                      flightresource.AirportLabelResource).delete()

    def iis_apdl(self, label):
        """机场整表同步"""
        return LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_AIRPORT_NESTED_SEQ,
                                      flightresource.AirportLabelResource).synchronization()


class IISBasicResourceMixin(IISGateResourceMixin,
                            IISBaggageResourceMixin,
                            IISCounterResourceMixin,
                            IISPlacementResourceMixin,
                            IISExceptionMixin,
                            IISCompanyMixin,
                            IISAirportMixin):
    """航班系统基础资源消息"""
    pass


class IISFlightMixin:
    """航班系统航班消息处理"""

    def iis_dfie(self, label):
        """航班动态增加"""
        LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_NESTED_SEQ, flight.FlightLabelResource).create()

    def iis_dfde(self, label):
        """航班动态删除"""
        LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_NESTED_SEQ, flight.FlightLabelResource).delete()

    def iis_dfdl(self, label):
        """航班整表同步事件"""
        LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_NESTED_SEQ, flight.FlightLabelResource).synchronization()

    def iis_update(self, label):
        """航班更新事件"""
        LabelResourceBulkProxy(label, MsgNestedSeq.FLIGHT_NESTED_SEQ, flight.FlightLabelResource).update()


def _iis_flight_monkey_patch():
    IISFlightMixin.iis_airl = IISFlightMixin.iis_update     # 航线变更
    IISFlightMixin.iis_hbtt = IISFlightMixin.iis_update     # 航班号变更
    IISFlightMixin.iis_arre = IISFlightMixin.iis_update     # 降落
    IISFlightMixin.iis_depe = IISFlightMixin.iis_update     # 起飞
    IISFlightMixin.iis_bore = IISFlightMixin.iis_update     # 开始登机
    IISFlightMixin.iis_poke = IISFlightMixin.iis_update     # 结束登机
    IISFlightMixin.iis_dlye = IISFlightMixin.iis_update     # 延误
    IISFlightMixin.iis_cane = IISFlightMixin.iis_update     # 取消
    IISFlightMixin.iis_rtne = IISFlightMixin.iis_update     # 返航
    IISFlightMixin.iis_bake = IISFlightMixin.iis_update     # 滑回
    IISFlightMixin.iis_alte = IISFlightMixin.iis_update     # 备降
    IISFlightMixin.iis_gtls = IISFlightMixin.iis_update     # 登机门更新
    IISFlightMixin.iis_blls = IISFlightMixin.iis_update     # 转盘更新
    IISFlightMixin.iis_stls = IISFlightMixin.iis_update     # 机位更新
    IISFlightMixin.iis_fptt = IISFlightMixin.iis_update     # 计划时间事件
    IISFlightMixin.iis_fett = IISFlightMixin.iis_update     # 预计时间事件
    IISFlightMixin.iis_frtt = IISFlightMixin.iis_update     # 实际时间事件
    IISFlightMixin.iis_trml = IISFlightMixin.iis_update     # 航站楼变更
    IISFlightMixin.iis_fatt = IISFlightMixin.iis_update     # 航班属性变更


_iis_flight_monkey_patch()
