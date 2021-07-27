"""
事件模块api
包含事件上报、事件统计、事件记录、事件导出相关接口
"""
import math
import datetime
from collections import OrderedDict

from rest_framework import status
from six import BytesIO
from xlwt import Workbook
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.db import connection
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed

from configurations.models import SystemConfig
from devices.models import DeviceInfo
from events import models
from events import serializers
from events.models import AlarmEvent, DeviceAlarmEvent, PersonAlarmEvent, EventWorkSheet
from events.utils import EventStatistics, HistoryStatistics
from situations.filter import DeployAlarmFilter
from situations.models import ResourceInfo
from security_platform import ErrorType, RET
from security_platform.utils import views
from security_platform.utils.commen import datetime_to_str
from security_platform.utils.filters import CustomDjangoFilterBackend
from security_platform.utils.viewsets import CustomModelViewSet


class AlarmEventViewSet(CustomModelViewSet):
    """
    安保事件视图集
    """
    serializer_class = serializers.AlarmEventSerializer
    queryset = AlarmEvent.objects.all().select_related(
        'devicealarmevent__device',
        'personalarmevent',
    ).prefetch_related('eventworksheet_set')

    def __init__(self, **kwargs):
        self.HistoryStatistics = HistoryStatistics
        self.EventStatistics = EventStatistics
        self.filter_data = None
        self._data = None
        self.instance = None
        self.event_days_data = []
        self.count_days_list = []
        self.event_months_data = []
        self.count_months_list = []
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data

            if 'event_name' in filter_data:
                filter_data['event_name__contains'] = filter_data.pop('event_name')

            if 'event_code' in filter_data:
                filter_data['event_code__contains'] = filter_data.pop('event_code')

            if filter_data.get('start_time'):
                filter_data['alarm_time__gte'] = filter_data.pop('start_time')

            if filter_data.get('end_time'):
                filter_data['alarm_time__lte'] = filter_data.pop('end_time')

            query_set = queryset.filter(**filter_data).order_by('-alarm_time')
        else:
            query_set = super().filter_queryset(queryset).order_by('-alarm_time')

        return query_set

    def get_serializer_class(self):
        """根据场景值返回对应的序列化器类"""
        event_type = self.request.query_params.get('event_type')
        if event_type and event_type.isdigit():
            event_type = int(event_type)
        else:
            return self.serializer_class

        if event_type == AlarmEvent.EventType.DEVICE:
            return serializers.DeviceAlarmEventSerializer
        elif event_type == AlarmEvent.EventType.ARTIFICIAL:
            return serializers.PersonAlarmEventListSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        """根据场景值返回对应的查询集"""
        if self.filter_data is None or self.filter_data.get('event_type') is None:
            return self.queryset
        elif self.filter_data['event_type'] == AlarmEvent.EventType.DEVICE:
            return DeviceAlarmEvent.objects.all()
        elif self.filter_data['event_type'] == AlarmEvent.EventType.ARTIFICIAL:
            return PersonAlarmEvent.objects.all()
        else:
            # 事件类型待定 先返回基础报警事件
            return self.queryset

    def list(self, request, *args, **kwargs):
        """
        事件列表
        """

        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.filter_data = serializer.validated_data
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """获取事件组详情"""
        instance = self.get_object()

        if instance.event_type == AlarmEvent.EventType.DEVICE:
            # 系统报警事件
            self.serializer_class = serializers.DeviceAlarmEventSerializer
        elif instance.event_type == AlarmEvent.EventType.ARTIFICIAL:
            # 人工上报事件
            self.serializer_class = serializers.PersonAlarmEventSerializer

        self.queryset = self.serializer_class.Meta.model.objects.only('id').all()
        instance = self.get_object()

        # 序列化
        serializer = self.get_serializer(instance)

        return self.success_response(data=serializer.data)

    @action(methods=['get'], detail=False)
    def exports(self, request, *args, **kwargs):
        """导出当前页数据为excel文件"""
        list_response = self.list(request, *args, **kwargs)
        data = list_response.data['objects']
        if not data:
            return self.structure_empty_excel_data()

        self._data = data

        work_book = self.structure_excel_data()
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('alarm_event_info.xls')
        response.write(sio.getvalue())

        return response

    @action(methods=['patch'], detail=True)
    def person(self, request, *args, **kwargs):
        """人工上报事件审核"""
        self.serializer_class = serializers.AuditPersonAlarmEventSerializer
        self.queryset = self.serializer_class.Meta.model.objects.only('id').all()
        return super().update(request, *args, **kwargs)

    @action(methods=['patch'], detail=True)
    def device(self, request, *args, **kwargs):
        """自动上报事件审核"""
        self.serializer_class = serializers.AuditDeviceAlarmEventSerializer
        self.queryset = self.serializer_class.Meta.model.objects.only('id').all()
        return super().update(request, *args, **kwargs)

    @action(methods=['patch'], detail=True)
    def confirm(self, request, *args, **kwargs):
        """系统报警事件确认"""
        self.serializer_class = serializers.DeviceAlarmConfirmEventSerializer
        self.queryset = self.serializer_class.Meta.model.objects.only('id').all()
        request.data['event_state'] = DeviceAlarmEvent.EventState.UNCONFIRMED
        return super().update(request, *args, **kwargs)

    @action(methods=['patch'], detail=True)
    def dispose(self, request, *args, **kwargs):
        """系统报警事件处置"""
        self.serializer_class = serializers.DeviceAlarmDisposeEventSerializer
        self.queryset = self.serializer_class.Meta.model.objects.only('id').all()
        return super().update(request, *args, **kwargs)

    @action(methods=['post'], detail=False)
    def persons(self, request, *args, **kwargs):
        """新增人工快捷上报事件"""
        self.serializer_class = serializers.PersonAlarmEventSerializer

        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def statistics(self, _):
        """
        根据类型/系统/等级对事件数据统计
        """

        # 查询统计数据
        priority_data = self.priority_statistics()
        alarm_type_data = self.alarm_type_statistics()
        belong_system_data = self.belong_system_statistics()

        # 构造数据
        priority_count_list = self.structure_priority_data(priority_data)
        alarm_type_count_list = self.structure_alarm_type_data(alarm_type_data)
        belong_system_count_list = self.structure_belong_system_data(belong_system_data)

        data = OrderedDict()
        data['priority_data'] = priority_count_list
        data['alarm_type_data'] = alarm_type_count_list
        data['belong_system_data'] = belong_system_count_list

        return self.success_response(data=data)

    @action(methods=['get'], detail=False)
    def days(self, request):
        """
        根据日期间隔对事件数量统计
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        format_start_date, format_end_date = self.validate_date(start_date), self.validate_date(end_date)

        if format_start_date > format_end_date:
            self.param_error(param_name='start_date或end_date', errmsg='开始日期不应大于结束日期')

        if not end_date:
            # 获取结束月份最后一天
            next_month = format_end_date.replace(day=28) + datetime.timedelta(days=4)
            format_end_date = next_month - datetime.timedelta(days=next_month.day)

        first_start_time = datetime.datetime.strptime('{0} 00:00:00'.format(format_start_date), "%Y-%m-%d %H:%M:%S")
        last_end_time = datetime.datetime.strptime('{0} {1}:59:59'.format(format_end_date, '23'), "%Y-%m-%d %H:%M:%S")

        query_data = self.interval_date(first_start_time, last_end_time)

        for son_data in query_data:
            # 构造查询数据列表、查询数据日期列表
            integration_data = OrderedDict()
            integration_data[self.HistoryStatistics.DATE] = son_data[0]
            integration_data[self.HistoryStatistics.COUNT] = son_data[1]
            self.event_days_data.append(integration_data)
            self.count_days_list.append(son_data[0])

        # 构造完整日期查询数据列表
        event_days_data = self.structure_date_range(start_date, end_date)

        return self.success_response(data=event_days_data)

    @action(methods=['get'], detail=False)
    def hours(self, request):
        """
        根据小时间隔对事件数量统计
        """

        now_date = datetime.datetime.today().date()

        first_start_time = datetime.datetime.strptime('{0} 00:00:00'.format(now_date), "%Y-%m-%d %H:%M:%S")
        last_end_time = datetime.datetime.strptime('{0} {1}:59:59'.format(now_date, '23'), "%Y-%m-%d %H:%M:%S")

        device_query_data = self.interval_hour_device(first_start_time, last_end_time)
        person_query_data = self.interval_hour_person(first_start_time, last_end_time)

        device_events_count = self.structure_device_hour_range(device_query_data)
        person_events_count = self.structure_person_hour_range(person_query_data)
        total_events_count = self.history_events_count()

        data = OrderedDict()
        data['device_events_count'] = device_events_count
        data['person_events_count'] = person_events_count
        data['total_events_count'] = total_events_count

        return self.success_response(data=data)

    @action(methods=['get'], detail=False)
    def months(self, request):
        """
        根据月份间隔对事件数量统计
        """
        start_month = request.query_params.get('start_month')
        end_month = request.query_params.get('end_month')
        start_date, end_date = self.validate_month(start_month), self.validate_month(end_month)
        if start_date > end_date:
            self.param_error(param_name='start_month或end_month', errmsg='开始月份不应大于结束月份')

        # 获取结束月份最后一天
        next_month = end_date.replace(day=28) + datetime.timedelta(days=4)
        end_date = next_month - datetime.timedelta(days=next_month.day)

        first_start_time = datetime.datetime.strptime('{0} 00:00:00'.format(start_date), "%Y-%m-%d %H:%M:%S")
        last_end_time = datetime.datetime.strptime('{0} {1}:59:59'.format(end_date, '23'), "%Y-%m-%d %H:%M:%S")

        query_data = self.interval_month(first_start_time, last_end_time)

        for son_data in query_data:
            # 构造查询数据列表、查询数据月份列表
            integration_data = OrderedDict()
            integration_data[self.HistoryStatistics.MONTH] = son_data[0]
            integration_data[self.HistoryStatistics.COUNT] = son_data[1]
            self.event_months_data.append(integration_data)
            self.count_months_list.append(son_data[0])

        # 构造完整月份查询数据列表
        event_months_data = self.structure_month_range(start_month, end_month)

        return self.success_response(data=event_months_data)

    def validate_date(self, date):
        """日期验证"""
        if date is None:
            self.param_error(param_name='start_date或end_date', code=ErrorType.NULL)
        if not date:
            now = datetime.date.today()
            date = str(datetime.datetime(now.year, now.month, 1).date())
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            self.param_error(code=ErrorType.INCORRECT_TYPE, param_name='start_date或end_date')

        return date

    def validate_month(self, month):
        """月份验证"""
        if month is None:
            self.param_error(param_name='start_month或end_month', code=ErrorType.NULL)
        if not month:
            self.param_error(param_name='start_month或end_month', code=ErrorType.BLANK)

        try:
            month = datetime.datetime.strptime(month, "%Y-%m").date()
        except (TypeError, ValueError):
            self.param_error(code=ErrorType.INCORRECT_TYPE, param_name='start_month或end_month')

        return month

    def interval_date(self, first_start_time, last_end_time):
        """按照日期统计事件数量"""
        with connection.cursor() as cursor:
            # 查询数据
            sql = 'select DATE_FORMAT(alarm_time,"{0}") {1},count(id) count from tb_basic_alarm_event where ' \
                  'alarm_time>="{2}" and alarm_time<="{3}" group by {1}'.format(self.HistoryStatistics.DATE_FORMAT,
                                                                                self.HistoryStatistics.DATE,
                                                                                first_start_time,
                                                                                last_end_time)
            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    def interval_month(self, first_start_time, last_end_time):
        """按照月份统计事件数量"""
        with connection.cursor() as cursor:
            # 查询数据
            sql = 'select DATE_FORMAT(alarm_time,"{0}") {1},count(id) count from tb_basic_alarm_event where ' \
                  'alarm_time>="{2}" and alarm_time<="{3}" group by {1}'.format(self.HistoryStatistics.MONTH_FORMAT,
                                                                                self.HistoryStatistics.MONTH,
                                                                                first_start_time,
                                                                                last_end_time)
            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    def structure_date_range(self, start_date, end_date):
        """构造日期间隔统计数据"""
        default_data_list = []
        real_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

        while start_date <= end_date:
            # 循环构造默认数据
            default_date_data = OrderedDict()
            default_date_data['date'] = start_date
            default_date_data['count'] = 0

            if start_date in self.count_days_list:
                # 如果默认日期数据查询日期列表中则替换数据
                for count_date_data in self.event_days_data:
                    if count_date_data['date'] == start_date:
                        default_date_data['count'] = count_date_data['count']

            default_data_list.append(default_date_data)
            real_date = real_date + datetime.timedelta(1)
            start_date = real_date.strftime("%Y-%m-%d")

        return default_data_list

    def structure_month_range(self, start_month, end_month):
        """构造月份间隔统计数据"""
        default_data_list = []
        real_month = datetime.datetime.strptime(start_month, "%Y-%m")

        while start_month <= end_month:
            # 循环构造默认数据
            default_date_data = OrderedDict()
            default_date_data['month'] = start_month
            default_date_data['count'] = 0

            if start_month in self.count_months_list:
                # 如果默认日期数据查询日期列表中则替换数据
                for count_date_data in self.event_months_data:
                    if count_date_data['month'] == start_month:
                        default_date_data['count'] = count_date_data['count']

            default_data_list.append(default_date_data)
            real_month = real_month + relativedelta(months=1)
            start_month = real_month.strftime("%Y-%m")

        return default_data_list

    def structure_device_hour_range(self, device_query_data):
        """初步构造系统上报事件数据结构"""
        device_events_count = []  # 系统上报事件总数据数组
        device_hour_list = []  # 按小时划分统计小时数组用于补充数据

        for device_count in device_query_data:
            # device_count 单条查询数据
            device_count_info = OrderedDict()  # 按小时划分统计总数据
            device_count_info['count_info'] = []  # 按小时划分统计数据数组
            device_count_info['belong_system_list'] = []  # 按小时划分统计归属系统数组，用于补充数据
            count_info = OrderedDict()  # 按小时划分统计数据对象

            # 构造小时信息
            device_count_info['hour'] = device_count[0]
            # 构造统计信息
            count_info['count'] = device_count[1]
            count_info['belong_system'] = device_count[2]

            if device_count[0] in device_hour_list:
                # 同一时间有不同系统统计事件，扩充统计信息、扩充系统信息
                device_events_count[- 1]['belong_system_list'].append(device_count[2])
                device_events_count[- 1]['count_info'].append(count_info)
            else:
                # 构造数据
                device_count_info['belong_system_list'].append(device_count[2])
                device_count_info['count_info'].append(count_info)
                device_events_count.append(device_count_info)

            if device_count[0] not in device_hour_list:
                # 构造小时数组
                device_hour_list.append(device_count[0])

        for info in device_events_count:
            # 循环获取构造之后的数据
            for belong_system in DeviceInfo.BelongSystem.labels:
                # 获取所有系统，循环判断是否存在数据，不存在数据则补零
                if belong_system not in info['belong_system_list']:
                    # 构造数据结构
                    count_info = OrderedDict()
                    count_info['count'] = 0
                    count_info['belong_system'] = belong_system
                    info['count_info'].append(count_info)
            # 删除冗余数据
            del info['belong_system_list']
        return self.complete_structure_device_hour_range(device_events_count, device_hour_list)

    @staticmethod
    def structure_person_hour_range(person_query_data):
        """构造人工上报事件数据结构"""
        person_events_count = []  # 人工上报事件总数据数组
        person_hour_list = []  # 按小时划分统计小时数组用于补充数据

        for person_count in person_query_data:
            # person_count 单条查询数据

            person_count_info = OrderedDict()
            # 构造数据
            person_count_info['hour'] = person_count[0]
            person_count_info['count'] = person_count[1]

            person_hour_list.append(person_count[0])
            person_events_count.append(person_count_info)

        for hour in range(24):
            # 循环获取构造之后的数据
            if hour not in person_hour_list:
                # 补充数据结构
                count_info = OrderedDict()
                count_info['hour'] = hour
                count_info['count'] = 0
                person_events_count.append(count_info)

        # 按照时间段排序
        person_events_count = sorted(person_events_count, key=lambda x: x['hour'], reverse=False)

        return person_events_count

    @staticmethod
    def complete_structure_device_hour_range(device_events_count, device_hour_list):
        """构造完整系统上报事件数据结构"""
        default_belong_system = []  # 默认系统统计数据数组

        for belong_system in DeviceInfo.BelongSystem.labels:
            default_belong_system_count = OrderedDict()  # 默认系统统计数据对象
            default_belong_system_count['count'] = 0
            default_belong_system_count['belong_system'] = belong_system
            default_belong_system.append(default_belong_system_count)

        for hour in range(24):
            count_info = OrderedDict()  # 默认系统上报事件统计对象
            count_info['hour'] = hour
            count_info['count_info'] = default_belong_system
            if hour not in device_hour_list:
                # 补全其他时间段数据
                device_events_count.append(count_info)

        # 按照时间段排序
        device_events_count = sorted(device_events_count, key=lambda x: x['hour'], reverse=False)

        return device_events_count

    def belong_system_statistics(self):
        """统计事件归属系统事件数量"""
        with connection.cursor() as cursor:
            sql = 'select {0}, count({1}) from tb_system_alarm_event  group by {0}'.format(
                self.EventStatistics.BELONG_SYSTEM, self.EventStatistics.PTR_ID)

            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    def alarm_type_statistics(self):
        """统计报警类型数量"""
        with connection.cursor() as cursor:
            sql = 'select {0}, count({1}) from tb_system_alarm_event where belong_system="{2}" group by {0}'.format(
                self.EventStatistics.ALARM_TYPE, self.EventStatistics.PTR_ID, DeviceInfo.BelongSystem.ANALYSIS.label)

            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    def priority_statistics(self):
        """统计事件等级数量"""
        with connection.cursor() as cursor:
            sql = 'select {0}, count({1}) from tb_basic_alarm_event  group by {0}'.format(
                self.EventStatistics.PRIORITY, self.EventStatistics.ID)

            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    def structure_priority_data(self, priority_data):
        """构造事件等级数据"""
        count_list = []
        priority_list = []

        for count_info in priority_data:
            # 构造查询数据
            count_dict = OrderedDict()
            count_dict[self.EventStatistics.PRIORITY] = count_info[0]
            count_dict[self.EventStatistics.COUNT] = count_info[1]
            count_list.append(count_dict)
            priority_list.append(count_info[0])

        for priority in range(1, 5):
            # 构造默认数据
            priority_dict = OrderedDict()
            priority_dict[self.EventStatistics.PRIORITY] = priority
            priority_dict[self.EventStatistics.COUNT] = 0

            # 补全数据
            if priority not in priority_list:
                count_list.append(priority_dict)
        return count_list

    def structure_alarm_type_data(self, alarm_type_data):
        """构造事件类型数据"""
        count_list = []

        for count_info in alarm_type_data:
            count_dict = OrderedDict()
            count_dict[self.EventStatistics.ALARM_TYPE] = count_info[0]
            count_dict[self.EventStatistics.COUNT] = count_info[1]
            count_list.append(count_dict)

        return count_list

    def structure_belong_system_data(self, belong_system_data):
        """构造事件归属系统数据"""
        count_list = []
        belong_system_list = []
        dict_data = dict(belong_system_data)
        dict_keys = list(dict_data.keys())
        dict_choices = DeviceInfo.BelongSystem.dict_choices

        # 归属系统中文转英文，如果中英文数据同时存在，则转英文后数据相加
        for key, value in dict_choices.items():
            if value in dict_keys:
                if key in dict_keys:
                    dict_data[key] = dict_data[key] + dict_data[value]
                else:
                    dict_data[key] = dict_data[value]
                del dict_data[value]

        belong_system_data = tuple(dict_data.items())

        for count_info in belong_system_data:
            # 构造查询数据
            count_dict = OrderedDict()
            count_dict[self.EventStatistics.BELONG_SYSTEM] = count_info[0]
            count_dict[self.EventStatistics.COUNT] = count_info[1]
            count_list.append(count_dict)
            belong_system_list.append(count_info[0])

        for belong_system in DeviceInfo.BelongSystem:
            # 构造默认数据
            belong_system_dict = OrderedDict()
            belong_system_dict[self.EventStatistics.BELONG_SYSTEM] = belong_system
            belong_system_dict[self.EventStatistics.COUNT] = 0

            # 补全数据
            if belong_system not in belong_system_list:
                count_list.append(belong_system_dict)

        return count_list

    def structure_excel_data(self):
        """构造excel数据"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'基础报警事件')
        work_book_data.write(0, 0, '事件名称')
        work_book_data.write(0, 1, u'事件编号')
        work_book_data.write(0, 2, u'报警时间')
        work_book_data.write(0, 3, u'所属区域')
        work_book_data.write(0, 4, u'所属楼层')
        work_book_data.write(0, 5, u'事件等级')
        work_book_data.write(0, 6, u'状态')
        work_book_data.write(0, 7, u'事件位置')
        work_book_data.write(0, 8, u'事件描述')
        work_book_data.write(0, 9, u'事件类型')
        # 写入数据
        excel_row = 1
        for event_info in self._data:
            data_name = event_info['event_name']
            data_code = event_info['event_code']
            data_time = event_info['alarm_time']
            data_area_code = event_info['area_code']
            data_floor_code = event_info['floor_code']
            data_priority = event_info['priority']
            event_state = event_info['event_state']
            event_type = AlarmEvent.event_type_label(event_info['event_type'])
            if event_state in PersonAlarmEvent.EventState.values:
                event_state = PersonAlarmEvent.event_state_label(event_state)
            else:
                event_state = DeviceAlarmEvent.event_state_label(event_state)

            data_event_state = event_state
            data_location_detail = event_info['location_detail']
            data_event_description = event_info['event_description']

            work_book_data.write(excel_row, 0, data_name)
            work_book_data.write(excel_row, 1, data_code)
            work_book_data.write(excel_row, 2, data_time)
            work_book_data.write(excel_row, 3, data_area_code)
            work_book_data.write(excel_row, 4, data_floor_code)
            work_book_data.write(excel_row, 5, data_priority)
            work_book_data.write(excel_row, 6, data_event_state)
            work_book_data.write(excel_row, 7, data_location_detail)
            work_book_data.write(excel_row, 8, data_event_description)
            work_book_data.write(excel_row, 9, event_type)

            excel_row += 1

        # ws.save("alarm_event_info.xls")

        return work_book

    @staticmethod
    def structure_empty_excel_data():
        """构造excel数据模板"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'基础报警事件')
        work_book_data.write(0, 0, '事件名称')
        work_book_data.write(0, 1, u'事件编号')
        work_book_data.write(0, 2, u'报警时间')
        work_book_data.write(0, 3, u'所属区域')
        work_book_data.write(0, 4, u'所属楼层')
        work_book_data.write(0, 5, u'事件等级')
        work_book_data.write(0, 6, u'状态')
        work_book_data.write(0, 7, u'事件位置')
        work_book_data.write(0, 8, u'事件描述')
        work_book_data.write(0, 9, u'事件类型')
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('alarm_event_info.xls')
        response.write(sio.getvalue())

        return response

    @staticmethod
    def interval_hour_person(first_start_time, last_end_time):
        """按照小时统计人工上报事件数量"""
        with connection.cursor() as cursor:
            # 查询数据
            sql = 'select HOUR(alarm_time) as Hour,count(*) as Count, "PERSON" as event_type from ' \
                  'tb_basic_alarm_event where alarm_time>="{0}" and alarm_time<="{1}" and event_type = 2 group by ' \
                  'HOUR(alarm_time),tb_basic_alarm_event.event_type'.format(first_start_time, last_end_time)
            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    @staticmethod
    def interval_hour_device(first_start_time, last_end_time):
        """按照小时统计自动上报事件数量"""
        with connection.cursor() as cursor:
            # 查询数据
            sql = 'select HOUR(alarm_time) as Hour,count(*) as Count,belong_system from tb_system_alarm_event as s ' \
                  'inner join tb_basic_alarm_event as b on (s.alarmevent_ptr_id=b.id) where (' \
                  'b.alarm_time>="{0}" and b.alarm_time<="{1}" and b.event_type = 1) group by HOUR(alarm_time),' \
                  'belong_system'.format(first_start_time, last_end_time)
            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    @staticmethod
    def history_events_count():
        """历史事件总数统计"""
        total_count = AlarmEvent.objects.all().only('id').count()
        relieved_count = AlarmEvent.objects.filter(Q(event_state=PersonAlarmEvent.EventState.AUDITED) |
                                                   Q(event_state=DeviceAlarmEvent.EventState.RELIEVED)).only(
            'id').count()
        total_count_info = OrderedDict()
        total_count_info['total_count'] = total_count
        total_count_info['relieved_count'] = relieved_count

        return total_count_info

    def create(self, request, *args, **kwargs):
        """禁止POST请求创建基础报警事件"""
        raise MethodNotAllowed(self.request.method)

    def update(self, request, *args, **kwargs):
        """禁止PUT请求修改事件参数"""
        raise MethodNotAllowed(self.request.method)

    def destroy(self, request, *args, **kwargs):
        """禁止DELETE请求删除事件数据"""
        raise MethodNotAllowed(self.request.method)


class AlarmEventWorkSheetView(views.CreateListCustomAPIView):
    """
    事件工单列表
    GET:工单列表
    POST：指派工单
    默认只能管理员或者更高级指派给同部门员工，支持批量指派给同一员工
    """
    serializer_class = serializers.AlarmEventWorkSheetSerializer
    queryset = EventWorkSheet.objects.only('id').all().order_by('-id'). \
        only('alarm_event__event_name', 'alarm_event__area_code', 'alarm_event__event_state', 'alarm_event__priority',
             'dispose_user__username', 'alarm_event_id', 'dispose_user_id').select_related('alarm_event',
                                                                                           'dispose_user')

    def __init__(self, **kwargs):
        self.filter_data = None
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data
            alarm_event = filter_data.get('alarm_event')
            dispose_user = filter_data.get('dispose_user')
            if alarm_event:
                if 'event_name' in alarm_event:
                    filter_data['alarm_event__event_name__contains'] = alarm_event.get('event_name')
                if 'event_code' in alarm_event:
                    filter_data['alarm_event__event_code__contains'] = alarm_event.get('event_code')
                if 'priority' in alarm_event:
                    filter_data['alarm_event__priority'] = alarm_event.get('priority')
                if 'event_type' in alarm_event:
                    filter_data['alarm_event__event_type'] = alarm_event.get('event_type')
                filter_data.pop('alarm_event')
            if dispose_user:
                if 'username' in dispose_user:
                    filter_data['dispose_user__username__contains'] = dispose_user.get('username')
                if 'id' in dispose_user:
                    filter_data['dispose_user_id'] = dispose_user.get('id')
                filter_data.pop('dispose_user')
            if filter_data.get('work_sheet_code'):
                filter_data['work_sheet_code__contains'] = filter_data.pop('work_sheet_code')
            if filter_data.get('start_time'):
                filter_data['alarm_event__alarm_time__gte'] = filter_data.pop('start_time')
            if filter_data.get('end_time'):
                filter_data['alarm_event__alarm_time__lte'] = filter_data.pop('end_time')
            if 'close_user' in filter_data:
                filter_data['close_user__contains'] = filter_data.pop('close_user')
            queryset = queryset.filter(**filter_data)

        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        """根据请求方式返回对应的序列化器类"""
        if self.request.method == 'GET':
            return serializers.AlarmEventWorkSheetListSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        """
        工单列表
        """

        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.filter_data = serializer.validated_data
        return super().list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """单条创建"""
        if isinstance(request.data, dict):
            return super().post(request, *args, **kwargs)
        return self.bulk_create(request, *args, **kwargs)

    def bulk_create(self, request, *args, **kwargs):
        """批量创建"""
        if not request.data:
            self.param_error(errcode=RET.PARSEERR)
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.validate_batch_serializer_data(serializer)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return self.success_response(serializer.data, status_code=status.HTTP_201_CREATED, headers=headers)

    def validate_batch_serializer_data(self, serializer):
        """格式化之外的序列化校验"""
        user_list = [validated_data.get('dispose_user') for validated_data in
                     serializer.validated_data]
        event_list = [validated_data.get('alarm_event') for validated_data in
                      serializer.validated_data]
        # 如果指定了多个不同的用户则抛出内部异常
        if len(set(user_list)) > 1:
            self.param_error(param_name='dispose_user_id')
        # 如果指定了多个相同的事件则抛出内部异常
        if len(set(event_list)) != len(event_list):
            self.param_error(param_name='event_id')
        return serializer.validated_data


class AlarmEventWorkSheetCloseView(views.RetrieveUpdateCustomAPIView):
    """
    事件工单关闭
    PUT:误派销单
    """
    serializer_class = serializers.AlarmEventWorkSheetCloseSerializer
    queryset = EventWorkSheet.objects.only('id').all().order_by('-id')

    def get_serializer_class(self):
        """根据请求方式返回对应的序列化器类"""
        if self.request.method == 'GET':
            return serializers.AlarmEventWorkSheetListSerializer
        return self.serializer_class


class UserAlarmEventWorkSheetView(views.CustomGenericAPIView):
    """
    当前用户已指派的待处置事件ID列表
    GET:当前用户已指派的待处置事件ID列表
    """

    def get_user_data(self):
        """获取用户信息"""
        user_data = OrderedDict()
        user = self.request.user
        user_data['user_id'] = user.id
        user_data['username'] = user.username

        return user_data

    @property
    def get_alarm_event_work_sheet(self):
        """获取事件对应工单"""
        alarm_event_work_sheet_data = OrderedDict()
        user = self.request.user
        event_id_list = EventWorkSheet.objects.filter(dispose_user=user, alarm_event__event_type=AlarmEvent.
                                                      EventType.DEVICE, sheet_state=EventWorkSheet.SheetState.
                                                      UNAUDITED).values_list('alarm_event_id', flat=True)
        alarm_event_work_sheet_data['event_id_list'] = list(event_id_list)
        return alarm_event_work_sheet_data

    def get(self, _):
        """获取用户指派的自动上报事件"""
        data = OrderedDict()
        data.update(self.get_user_data())
        data.update(self.get_alarm_event_work_sheet)

        return self.success_response(data=data)


class QueueStatisticsView(views.CustomGenericAPIView):
    """排队统计"""

    queryset = models.CameraLineUpRecord.objects.all()

    def get_queue_number(self, resource_type):
        """获取排队数据

        数据有效期为5分钟, 5分钟内不存在排队数据则为0

        Args:
            resource_type: 资源类型

        Returns:

        """
        return self.queryset.filter(
            camera__resource__resource_type=resource_type,
            detection_time__gte=datetime.datetime.now() - datetime.timedelta(minutes=models.CameraLineUpRecord.expire)
        ).aggregate(total_people=Sum('current_queue_number'))['total_people'] or 0

    def get(self, _):
        """态势首页排队总数

        security_queue_count: 安检口当天的排队总人数
        counter_queue_count: 值机柜台当天的排队总人数
        """
        data = OrderedDict()
        data['security_queue_count'] = self.get_queue_number(ResourceInfo.ResourceType.SECURITY)
        data['counter_queue_count'] = self.get_queue_number(ResourceInfo.ResourceType.COUNTER)

        return self.success_response(data=data)


# noinspection PyUnresolvedReferences, PyAttributeOutsideInit
class ResourceTypeMixin:
    """资源类型工具类

    提供资源类型参数的校验及获取
    资源类型必传
    """

    @property
    def resource_type(self):
        """资源类型"""
        if not hasattr(self, '_resource_type'):
            self._resource_type = self.validate_resource_type()

        return self._resource_type

    def validate_resource_type(self):
        """资源类型校验"""
        resource_type = self.request.query_params.get('resource_type')

        if resource_type is None:
            self.param_error(param_name='resource_type', code=ErrorType.REQUIRED)

        if resource_type not in ResourceInfo.ResourceType:
            self.param_error(param_name='resource_type')

        return resource_type


class PassengerFlowView(views.CustomGenericAPIView, ResourceTypeMixin):
    """客流分析视图

    返回曲线图数据、总人数、速度
    """

    WEEK_COUNT = 4
    PREDICTED_CACHE_DATA_EXPIRE = 86400
    PREDICTED_CACHE_KEY = '{resource_type}_predicted_{current_time_date}'

    @property
    def current_time(self):
        """当前时间"""
        if not hasattr(self, '_current_time'):
            self._current_time = datetime.datetime.now()

        return self._current_time

    def create_days_data(self):
        """客流统计数据

        Returns:
            客流模版数据
            Examples：
                00:00:00: 0
                01:00:00: 10
                02:00:00: 20
                ...
                23:59:59: 200
        """
        time_data = OrderedDict()

        for i in range(25):
            # i-> 0-24
            if i < 24:
                # 0-23点
                time_data[f'{i:02d}:00:00'] = 0
            else:
                # 24点
                time_data['23:59:59'] = 0

        return time_data

    def get_filter_kwargs(self):
        """获取查询集过滤字段

        出入口数据只对入口进行统计，出口不进行统计
        """
        filter_kwargs = OrderedDict()
        filter_kwargs['camera__resource__resource_type'] = self.resource_type

        if self.resource_type == ResourceInfo.ResourceType.PASSAGEWAY:
            filter_kwargs['camera__resource__resource_type_sec'] = ResourceInfo.ResourceTypeSecond.ENTRANCE

        return filter_kwargs

    def get_current_aggregate_data(self):
        """获取实时聚合人数统计数据"""
        filter_kwargs = self.get_filter_kwargs()
        filter_kwargs['statistical_time__gte'] = self.current_time.date()

        return models.PeopleCountingRecord.objects.filter(**filter_kwargs).values(
            'statistical_time').annotate(total_people=Sum('total_people'))

    def get_predicted_aggregate_data(self):
        """获取预测聚合人数统计数据

        根据当前时间的星期数获取历史4周内的数据，取平均值计算

        Returns：
            实时人数统计数据字典
        """
        filter_kwargs = self.get_filter_kwargs()
        filter_kwargs['statistical_time__week_day'] = self.current_time.weekday() + 2
        filter_kwargs['statistical_time__lt'] = self.current_time.date()
        filter_kwargs['statistical_time__gte'] = self.current_time.date() - datetime.timedelta(days=self.WEEK_COUNT * 7)

        return models.PeopleCountingRecord.objects.filter(**filter_kwargs).extra(
            select={"time": "DATE_FORMAT(statistical_time, '%%H:%%i:%%s')"}
        ).values('time').annotate(total_people=Sum('total_people'))

    def get_current_data(self):
        """获取实时人数统计数据

        Returns:
            实时数据字典, 包含曲线图数据，总人数，速度
        """
        current_data = OrderedDict()
        hour = self.current_time.hour + (self.current_time.minute / 60)

        people_current_data = self.get_current_aggregate_data()
        current_data['current_data'] = self.create_days_data()
        current_data['current_total_people_number'] = 0

        for row_data in people_current_data:
            current_data['current_total_people_number'] += int(row_data['total_people'])
            current_data['current_data'][datetime_to_str(row_data['statistical_time'], date_format='%H:%M:%S')] += int(
                row_data['total_people'])

        if hour > 0:
            current_data['current_speed'] = math.ceil(
                current_data['current_total_people_number'] / hour)
        else:
            current_data['current_speed'] = current_data['current_total_people_number']

        return current_data

    def get_open_count(self, predicted_data):
        """预测开通个数"""
        statistical_time = str(models.PeopleCountingRecord.time_to_statistical_time(self.current_time).time())
        security_speed = SystemConfig.objects.get(config_key=SystemConfig.ConfigKey.SECURITY_SPEED).value

        return math.ceil(predicted_data['predicted_data'][statistical_time] / security_speed)

    def get_predicted_data(self):
        """获取预测数据

        使用redis缓存当天的预测数据，如果缓存不存在就获取后写入缓存
        缓存有效期为24小时
        缓存的key根据资源类型和当前时间使用格式化字符串
        PREDICTED_CACHE_KEY = '{resource_type}_predicted_{current_time_date}'

        Returns:
            预测数据字典, 包含曲线图数据，总人数，速度
        """
        cache_key = self.PREDICTED_CACHE_KEY.format(
            resource_type=self.resource_type,
            current_time_date=str(self.current_time.date())
        )

        predicted_data = cache.get(cache_key)
        # predicted_data = None
        if not predicted_data:
            predicted_data = self._get_predicted_data()
            cache.set(cache_key, predicted_data, self.PREDICTED_CACHE_DATA_EXPIRE)

        # 安检口开通个数
        # predicted_data['predicted_open_count'] = self.get_open_count(predicted_data)

        return predicted_data

    def _get_predicted_data(self):
        """获取历史预测数据

        Returns:
            预测数据字典, 包含曲线图数据，总人数，速度
        """
        predicted_data = OrderedDict()
        predicted_aggregate_data = self.get_predicted_aggregate_data()
        predicted_data['predicted_data'] = self.create_days_data()
        predicted_data['predicted_total_people_number'] = 0

        for row_data in predicted_aggregate_data:
            time_ = row_data['time']
            if '59' in time_:
                time_ = '23:59:59'

            predicted_data['predicted_data'][time_] += math.ceil(row_data['total_people'] / self.WEEK_COUNT)
            predicted_data['predicted_total_people_number'] += math.ceil(row_data['total_people'] / self.WEEK_COUNT)

        predicted_data['predicted_speed'] = math.ceil(predicted_data['predicted_total_people_number'] / 24)

        return predicted_data

    def get(self, _):
        """预测及实时人数统计数据获取"""
        data = OrderedDict()
        data.update(self.get_current_data())
        data.update(self.get_predicted_data())

        return self.success_response(data=data)


class DeploySnapView(views.ListCustomAPIView, ResourceTypeMixin):
    """布控抓拍"""

    serializer_class = serializers.DeploySnapSerializer
    queryset = models.DeployPersonSnapRecord.objects.all()

    def get_queryset(self):
        """根据资源类型过滤查询集"""
        return self.queryset.filter(camera__resource__resource_type=self.resource_type).only(
            'snap_time',
            'snap_image_url',
            'camera__resource__name',
            'camera__resource__resource_type',
            'camera__resource_id',
        ).select_related('camera__resource').order_by('-id')


class DeployAlarmView(views.ListCustomAPIView, ResourceTypeMixin):
    """布控报警"""

    serializer_class = serializers.DeployAlarmSerializer
    queryset = models.DeployAlarmRecord.objects.all().order_by('-id').select_related('event', 'resource')
    filter_backends = (CustomDjangoFilterBackend,)
    filter_class = DeployAlarmFilter


class DensityAlarmView(views.ListCustomAPIView):
    """密度报警记录"""

    serializer_class = serializers.DensityAlarmSerializer
    queryset = models.PersonDensityRecord.objects.all()

    def get_queryset(self):
        """获取今天的报警数据"""
        filter_data = {'resource__resource_type': ResourceInfo.ResourceType.SECURITY_HALL}

        only_fields = [
            'total_people_number',
            'alarm_image_url',
            'event__id',
            'event__alarm_time',
            'event__priority',
            'event__device__device_name',
            'event__device__device_code',
            'event__device__cameradevice__flow_address'
        ]

        return self.queryset.filter(**filter_data).only(*only_fields).select_related(
            'event',
            'event__device',
            'event__device__cameradevice'
        ).order_by('-id')


class PostureAlarmView(views.ListCustomAPIView):
    """姿态动作识别报警列表"""

    serializer_class = serializers.PostureAlarmSerializer
    queryset = models.PostureAlarmRecord.objects.all()

    def get_queryset(self):
        """过滤原始查询集

        过滤出反向通道的所有报警,增加关联查询字段及排序

        Returns:
            queryset: 过滤后的资源查询集
        """
        filter_data = {'resource__resource_type': ResourceInfo.ResourceType.REVERSE}

        only_fields = [
            'alarm_image_url',
            'event__id',
            'event__alarm_time',
            'event__event_name',
            'resource__name',
            'resource__resource_type',
            'resource_id'
        ]

        return self.queryset.filter(**filter_data).only(*only_fields).select_related(
            'event', 'resource').order_by('-id')


class ScopesAlarmView(views.ListCustomAPIView):
    """围界设备报警记录

    围界系统的报警，走围界系统的MQ
    """

    serializer_class = serializers.ScopesAlarmSerializer
    queryset = models.DeviceAlarmEvent.objects.filter(
        belong_system=DeviceInfo.BelongSystem.MAINTENANCE).only(
        'event_name',
        'alarm_time',
        'area_code',
        'priority',
        'alarm_time',
        'device__device_name',
        'device__device_code'
    ).select_related('device').order_by('-id')


class MonitorScopesAlarmView(views.ListCustomAPIView):
    """围界设备报警记录

    围界系统的报警，走视频监控webapi版本
    """
    serializer_class = serializers.MonitorScopesAlarmSerializer
    queryset = models.DeviceAlarmEvent.objects.filter(
        event_name='围界报警',
        # belong_system=DeviceInfo.BelongSystem.CAMERA.label
    ).only(
        'event_name',
        'alarm_time',
        'area_code',
        'priority',
        'alarm_time',
        'device__device_name',
        'device__device_code',
        'device__cameradevice__flow_address'
    ).select_related('device', 'device__cameradevice').order_by('-id')


class PlacementAlarmView(views.ListCustomAPIView):
    """机位报警信息"""

    serializer_class = serializers.PlacementAlarmSerializer
    queryset = models.PlaceAlarmRecord.objects.all().order_by('-id').only(
        'resource__name',
        'resource__resource_type',
        'resource_id',
        'event__id',
        'event__alarm_time',
        'event__event_name'
    ).select_related('event', 'resource')


class PlacementSafeguardView(views.ListCustomAPIView):
    """机位保障信息"""

    serializer_class = serializers.PlacementSafeguardSerializer
    queryset = models.PlaceSafeguardRecord.objects.all().order_by('-id').only(
        'safeguard_name',
        'safeguard_time',
        'safeguard_image_url',
        'flight__flight_number',
        'camera__resource_id',
        'camera__resource__name',
        'camera__resource__resource_type'
    ).select_related('flight', 'camera__resource')
