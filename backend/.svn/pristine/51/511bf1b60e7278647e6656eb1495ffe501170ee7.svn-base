"""
事件模块序列化器
"""
import datetime

from django.db import transaction
from rest_framework import serializers

from users.models import UserDiary, UserBacklog
from events.models import (
    PersonAlarmEvent, AlarmEvent, DeviceAlarmEvent, DeployAlarmRecord,
    DeployPersonSnapRecord, PersonDensityRecord, BehaviorAlarmRecord,
    PlaceAlarmRecord, PlaceSafeguardRecord,
    EventWorkSheet)

from security_platform.utils.serializer import CustomModelSerializer, CustomCharField
from security_platform import ErrorType, RET


class AlarmEventSerializer(CustomModelSerializer):
    """基础报警事件序列化器"""
    start_time = serializers.DateTimeField(label='开始时间', required=False)
    end_time = serializers.DateTimeField(label='结束时间', required=False)
    gis_basic_info = serializers.SerializerMethodField()
    gis_field = serializers.SerializerMethodField()

    class Meta:
        model = AlarmEvent
        fields = (
            'event_id', 'event_name', 'event_type', 'event_code', 'alarm_time', 'area_code', 'event_state',
            'floor_code', 'priority', 'location_detail', 'event_description', 'start_time', 'end_time',
            'gis_basic_info', 'gis_field'
        )

        extra_kwargs = {
            'event_code': {
                'required': False,
                'validators': []
            },
            'event_name': {
                'allow_blank': True
            },
            'event_state': {
                'required': False,
            },
            # 'priority': {
            #     'max_value': 10,
            #     'min_value': 0,
            #     'required': True
            # },
            'event_id': {
                'read_only': True,
                'source': 'id'
            }
        }

    def get_gis_basic_info(self, instance):
        if instance.event_type == AlarmEvent.EventType.DEVICE:
            return instance.devicealarmevent.device.gis_basic_info

        return instance.personalarmevent.gis_basic_info

    def get_gis_field(self, instance):
        if instance.event_type == AlarmEvent.EventType.DEVICE:
            return instance.devicealarmevent.device.gis_field

        return instance.personalarmevent.gis_field

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('alarm_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            if key == 'event_type':
                if data[key] == AlarmEvent.EventType.DEVICE:
                    event_work_sheet_data = instance._prefetched_objects_cache.get('eventworksheet_set')
                    if event_work_sheet_data:
                        event_work_sheet = event_work_sheet_data.filter(sheet_state=EventWorkSheet.
                                                                        SheetState.UNAUDITED)
                        data['event_work_sheet_id'] = event_work_sheet[0].id if event_work_sheet else ''
                        data['event_work_sheet_code'] = event_work_sheet[0].work_sheet_code if event_work_sheet else ''
                    else:
                        data['event_work_sheet_id'] = ''
                        data['event_work_sheet_code'] = ''
                else:
                    data['event_work_sheet_id'] = ''
                    data['event_work_sheet_code'] = ''
        return data


class PersonAlarmEventListSerializer(CustomModelSerializer):
    """人工快捷上报事件列表序列化器"""
    start_time = serializers.DateTimeField(label='开始时间', required=False)
    end_time = serializers.DateTimeField(label='结束时间', required=False)

    class Meta:
        model = PersonAlarmEvent
        fields = (
            'event_id', 'event_name', 'event_type', 'event_code', 'alarm_time', 'area_code', 'event_state',
            'floor_code', 'priority', 'location_detail', 'event_description', 'alarm_person_name', 'alarm_person_type',
            'alarm_person_mobile', 'handled_user', 'handled_time', 'handled_opinion', 'audit_user', 'audit_time',
            'audit_opinion', 'gis_basic_info', 'gis_field', 'start_time', 'end_time'
        )

        extra_kwargs = {
            'event_code': {
                'required': False,
                'validators': []
            },
            'event_state': {
                'required': False,
            },
            'priority': {
                'required': False
            },
            'event_id': {
                'read_only': True,
                'source': 'id'
            },
            'handled_user': {
                'allow_null': False,
                'required': False
            },
            'event_name': {
                'required': False,
                'allow_blank': True
            },
            'handled_opinion': {
                'required': False
            },
        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('alarm_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            elif key.find('handled_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            elif key.find('audit_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data


class PersonAlarmEventSerializer(CustomModelSerializer):
    """人工快捷上报事件序列化器"""

    class Meta:
        model = PersonAlarmEvent
        fields = (
            'event_id', 'event_name', 'event_type', 'event_code', 'alarm_time', 'area_code', 'event_state',
            'floor_code', 'priority', 'location_detail', 'event_description', 'alarm_person_name', 'alarm_person_type',
            'alarm_person_mobile', 'handled_user', 'handled_time', 'handled_opinion', 'audit_user', 'audit_time',
            'audit_opinion', 'gis_basic_info', 'gis_field'
        )

        extra_kwargs = {
            'event_code': {
                'required': False
            },
            'event_state': {
                'required': False,
            },
            # 'priority': {
            #     'max_value': 10,
            #     'min_value': 0,
            #     'required': True
            # },
            'event_id': {
                'read_only': True,
                'source': 'id'
            },
            'handled_user': {
                'allow_null': False,
                'required': False
            },
            # 'handled_time': {
            #     'required': True,
            # },
            'handled_opinion': {
                'allow_null': False,
            },
        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('alarm_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            elif key.find('handled_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            elif key.find('audit_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data

    def create(self, validated_data):
        """
        事件上报
        """
        validated_data['event_code'] = PersonAlarmEvent.generate_event_code()
        validated_data['event_state'] = PersonAlarmEvent.EventState.UNAUDITED
        validated_data['event_type'] = AlarmEvent.EventType.ARTIFICIAL
        validated_data['handled_user'] = self.context["request"].user.username
        validated_data['handled_time'] = datetime.datetime.now()
        # 控制数据库事务交易
        with transaction.atomic():
            instance = super().create(validated_data)
            # 创建员工日志
            self.create_staff_diary(instance)
            # 创建工单
            event_work_sheet = self.create_event_work_sheet(instance)
            # 创建代办事项
            self.create_user_back_log(event_work_sheet)
        return instance

    def validate(self, attrs):
        """
        参数校验
        """
        handled_opinion = attrs.get('handled_opinion')
        gis_basic_info = attrs.get('gis_basic_info')
        gis_field = attrs.get('gis_field')
        if not handled_opinion:
            self.param_error(code=ErrorType.NULL, param_name='handled_opinion')
        if not gis_basic_info:
            self.param_error(code=ErrorType.NULL, param_name='gis_basic_info')
        if not gis_field:
            self.param_error(code=ErrorType.NULL, param_name='gis_field')

        return attrs

    def create_staff_diary(self, instance):
        """
        创建员工日志
        """
        UserDiary.objects.create(
            job_time=datetime.datetime.now(),
            user=self.context['request'].user,
            handover_user=self.context['request'].user,
            job_content='自动记录日志，处置人工上报事件{0}, 事件编号为{1}'.format(instance.event_name, instance.event_code),
            handover_content='自动记录日志，处置人工上报事件{0}, 事件编号为{1}'.format(instance.event_name, instance.event_code)
        )

    def create_event_work_sheet(self, instance):
        """
        创建事件工单
        """
        event_work_sheet = EventWorkSheet.objects.create(
            alarm_event=instance,
            work_sheet_code=EventWorkSheet.generate_work_sheet_code(),
            dispose_user=self.context["request"].user

        )
        return event_work_sheet

    def create_user_back_log(self, event_work_sheet):
        """创建用户代办事项"""
        UserBacklog.objects.create(
            object_id=event_work_sheet.id,
            user=self.context["request"].user,
            backlog_type=UserBacklog.BacklogType.event_worksheet,
            description='您有一条事件工单待处理')


class AuditPersonAlarmEventSerializer(CustomModelSerializer):
    """人工上报事件审核事件序列化器"""

    class Meta:
        model = PersonAlarmEvent
        fields = (
            'audit_user', 'audit_time', 'audit_opinion', 'event_state'
        )
        extra_kwargs = {

            'event_state': {
                'required': False,
            },

        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('audit_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data

    # noinspection PyUnresolvedReferences
    def update(self, instance, validated_data):
        """人工上报事件审核"""
        event_state = instance.event_state
        # 事件状态校验
        if event_state != PersonAlarmEvent.EventState.UNAUDITED:
            self.param_error(param_name=event_state, code=ErrorType.EVENT_STATE)
        # 控制数据库事务交易
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            # 更新事件工单状态为关闭
            event_work_sheet = instance.eventworksheet_set.first()
            if not event_work_sheet:
                self.param_error(errmsg='事件{0}工单不存在'.format(instance.event_name))
            event_work_sheet.sheet_state = EventWorkSheet.SheetState.CLOSED
            event_work_sheet.save()

            # 删除工单对应代办事项
            user_backlog = UserBacklog.objects.filter(object_id=instance.id).first()
            if user_backlog:
                user_backlog.delete()

        return instance

    def validate(self, attrs):
        """
        参数校验
        """
        audit_opinion = attrs.get('audit_opinion')

        if not audit_opinion:
            self.param_error(param_name='audit_opinion', code=ErrorType.NULL)

        attrs['audit_user'] = self.context["request"].user.username
        attrs['audit_time'] = datetime.datetime.now()
        attrs['event_state'] = PersonAlarmEvent.EventState.AUDITED

        return attrs


class AuditDeviceAlarmEventSerializer(CustomModelSerializer):
    """自动上报事件审核事件序列化器"""

    class Meta:
        model = DeviceAlarmEvent
        fields = (
            'audit_user', 'audit_time', 'audit_opinion', 'event_state'
        )
        extra_kwargs = {

            'event_state': {
                'read_only': True,
            },

        }

    # def to_representation(self, instance):
    #     """返回消息处理"""
    #     data = super().to_representation(instance)
    #
    #     for key in list(data.keys()):
    #         value = data[key]
    #         if value is None:
    #             data[key] = ''
    #             value = ''
    #
    #         if key.find('audit_time') != -1:
    #             data[key] = value.replace('T', ' ').split('.')[0]
    #
    #     return data

    # noinspection PyUnresolvedReferences
    def update(self, instance, validated_data):
        """自动上报事件审核"""
        event_state = instance.event_state
        # 事件状态校验
        if event_state != DeviceAlarmEvent.EventState.RELIEVED:
            self.param_error(param_name=event_state, code=ErrorType.EVENT_STATE)
        # 控制数据库事务交易
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            # 更新事件工单状态为关闭
            event_work_sheet = instance.eventworksheet_set.all().filter(sheet_state=EventWorkSheet.
                                                                        SheetState.UNAUDITED).first()
            if not event_work_sheet:
                self.param_error(errmsg='事件{0}工单不存在'.format(instance.event_name))
            event_work_sheet.sheet_state = EventWorkSheet.SheetState.CLOSED
            event_work_sheet.save()

            # 删除工单对应代办事项
            user_backlog = UserBacklog.objects.filter(object_id=instance.id).first()
            if user_backlog:
                user_backlog.delete()

        return instance

    def validate(self, attrs):
        """
        参数校验
        """
        audit_opinion = attrs.get('audit_opinion')

        if not audit_opinion:
            self.param_error(param_name='audit_opinion', code=ErrorType.NULL)

        attrs['audit_user'] = self.context["request"].user.username
        attrs['audit_time'] = datetime.datetime.now()

        return attrs


class DeviceAlarmEventSerializer(CustomModelSerializer):
    """设备快捷上报事件序列化器"""
    start_time = serializers.DateTimeField(label='开始时间', required=False)
    end_time = serializers.DateTimeField(label='结束时间', required=False)

    class Meta:
        model = DeviceAlarmEvent
        fields = (
            'event_id', 'event_name', 'event_type', 'event_code', 'alarm_time', 'area_code', 'event_state',
            'floor_code', 'priority', 'location_detail', 'event_description', 'subsystem_event_id', 'alarm_type',
            'device_id', 'belong_system', 'is_misrepresent', 'acknowledged_user', 'acknowledged_time',
            'acknowledged_opinion', 'dispose_user', 'dispose_time', 'dispose_opinion', 'pass_id', 'audit_user',
            'audit_time', 'audit_opinion', 'start_time', 'end_time'
        )

        extra_kwargs = {
            'belong_system': {
                'required': False,
            },
            'alarm_device_code': {
                'source': 'device'
            },
            'event_code': {
                'required': False,
                'validators': []
            },
            'event_state': {
                'required': False,
            },
            'priority': {
                'required': False
            },
            'event_id': {
                'read_only': True,
                'source': 'id'
            },
            'device_id': {
                'read_only': True,
                'source': 'device'
            },
            'event_name': {
                'required': False,
                'allow_blank': True
            },
        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''
            if key == 'device_id':
                # 补充设备字段、资源字段
                data['alarm_device_code'] = instance.device.device_code if instance.device else ''
                data['gis_basic_info'] = instance.device.gis_basic_info if instance.device else ''
                data['gis_field'] = instance.device.gis_field if instance.device else ''
                data['resource_id'] = instance.device.resource_id if instance.device.resource else ''
                data['resource_type'] = instance.device.resource.resource_type if instance.device.resource else ''
                data['resource_name'] = instance.device.resource.name if instance.device.resource else ''

            if key.find('alarm_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            elif key.find('acknowledged_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]
            elif key.find('dispose_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data

    def create(self, validated_data):
        """
        事件上报
        """
        validated_data['event_code'] = PersonAlarmEvent.generate_event_code()
        validated_data['event_state'] = DeviceAlarmEvent.EventState.UNCONFIRMED
        return super().create(validated_data)


class DeviceAlarmConfirmEventSerializer(CustomModelSerializer):
    """设备报警事件确认序列化器"""

    class Meta:
        model = DeviceAlarmEvent
        fields = (
            'event_state', 'is_misrepresent', 'acknowledged_user', 'acknowledged_time', 'acknowledged_opinion',
        )

    # noinspection PyUnresolvedReferences
    def update(self, instance, validated_data):
        """事件确认"""
        event_state = instance.event_state
        # 事件状态校验
        if event_state != DeviceAlarmEvent.EventState.UNCONFIRMED:
            self.param_error(param_name=event_state, code=ErrorType.EVENT_STATE)

        instance = super().update(instance, validated_data)

        return instance

    def validate(self, attrs):
        """
        参数校验
        """
        is_misrepresent = attrs.get('is_misrepresent')
        acknowledged_opinion = attrs.get('acknowledged_opinion')

        if is_misrepresent is None:
            self.param_error(param_name='is_misrepresent', code=ErrorType.BLANK)
        if acknowledged_opinion is None:
            self.param_error(param_name='acknowledged_opinion', code=ErrorType.NULL)

        attrs['acknowledged_user'] = self.context["request"].user.username
        attrs['acknowledged_time'] = datetime.datetime.now()
        attrs['acknowledged_opinion'] = acknowledged_opinion

        if is_misrepresent is True:
            attrs['event_state'] = DeviceAlarmEvent.EventState.RELIEVED
        else:
            attrs['event_state'] = DeviceAlarmEvent.EventState.UNDISPOSED

        return attrs

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('acknowledged_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data


class DeviceAlarmDisposeEventSerializer(CustomModelSerializer):
    """设备报警事件处置序列化器"""

    class Meta:
        model = DeviceAlarmEvent
        fields = (
            'event_state', 'dispose_user', 'dispose_time', 'dispose_opinion',
        )
        extra_kwargs = {

            'event_state': {
                'required': False,
            },

        }

    def update(self, instance, validated_data):
        """事件处置"""
        event_state = instance.event_state
        # 事件状态校验
        if event_state != DeviceAlarmEvent.EventState.UNDISPOSED:
            self.param_error(param_name=event_state, code=ErrorType.EVENT_STATE)
        # 控制数据库事务交易
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            # 创建员工日志
            self.create_staff_diary(instance)
        return instance

    def validate(self, attrs):
        """
        参数校验
        """
        dispose_opinion = attrs.get('dispose_opinion')

        if dispose_opinion is None:
            self.param_error(param_name='dispose_opinion', code=ErrorType.NULL)

        attrs['dispose_user'] = self.context["request"].user.username
        attrs['dispose_opinion'] = dispose_opinion
        attrs['dispose_time'] = datetime.datetime.now()
        attrs['event_state'] = DeviceAlarmEvent.EventState.RELIEVED
        return attrs

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('dispose_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data

    def create_staff_diary(self, instance):
        """
        创建员工日志
        """
        UserDiary.objects.create(
            job_time=datetime.datetime.now(),
            user=self.context['request'].user,
            handover_user=self.context['request'].user,
            job_content='自动记录日志，处置设备报警事件{0}, 事件编号为{1}'.format(instance.event_name, instance.event_code),
            handover_content='自动记录日志，处置设备报警事件{0}, 事件编号为{1}'.format(instance.event_name, instance.event_code)
        )


class AlarmEventWorkSheetSerializer(CustomModelSerializer):
    """事件工单新增序列化器"""
    event_name = serializers.CharField(source='alarm_event.event_name', required=False)
    event_code = serializers.CharField(source='alarm_event.event_code', required=False)
    event_state = serializers.CharField(source='alarm_event.event_state', required=False)
    priority = serializers.CharField(source='alarm_event.priority', required=False)

    class Meta:
        model = EventWorkSheet
        fields = (
            'event_work_sheet_id', 'work_sheet_code', 'sheet_state', 'event_name', 'event_code',
            'event_id', 'event_state', 'priority', 'event_type', 'dispose_user_id'
        )

        extra_kwargs = {
            'work_sheet_code': {
                'required': False,
            },
            'sheet_state': {
                'required': False,
            },
            'event_work_sheet_id': {
                'read_only': True,
                'source': 'id'
            },
            'event_id': {
                'source': 'alarm_event'
            },
            'dispose_user_id': {
                'source': 'dispose_user'
            },
        }

    def create(self, validated_data):
        """创建工单"""
        # 控制数据库事务交易
        with transaction.atomic():
            # 生成工单编号
            work_sheet_code = EventWorkSheet.generate_work_sheet_code()
            validated_data['work_sheet_code'] = work_sheet_code

            # 生成工单
            instance = super().create(validated_data)
            # 生成用户代办事项
            self.create_user_back_log(instance)
        return instance

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if data['dispose_user_id']:
                data['dispose_user_name'] = instance.dispose_user.username if instance.dispose_user else ''

        return data

    def validate_event_id(self, event_id):
        """校验是否为未处置的自动上报事件"""
        if event_id.event_type != AlarmEvent.EventType.DEVICE or event_id.event_state != \
                DeviceAlarmEvent.EventState.UNDISPOSED:
            self.param_error(param_name='event_id', code=ErrorType.INCORRECT_TYPE)

        return event_id

    def validate(self, attrs):
        """参数校验"""
        dispose_user = attrs.get('dispose_user')
        alarm_event = attrs.get('alarm_event')

        if not dispose_user:
            self.param_error(code=ErrorType.NULL, param_name='dispose_user_id')

        assigned_work_sheet = EventWorkSheet.objects.filter(alarm_event=alarm_event, sheet_state=EventWorkSheet.
                                                            SheetState.UNAUDITED).first()

        if assigned_work_sheet:
            self.param_error(errmsg='处置人{0}已指派事件{1}，请勿重复派单'.format(assigned_work_sheet.dispose_user.username,
                                                                   alarm_event.event_name),
                             errcode=RET.EXPARAMERR)
        return attrs

    def create_user_back_log(self, instance):
        """创建用户代办事项"""
        UserBacklog.objects.create(
            object_id=instance.id,
            user=self.context["request"].user,
            backlog_type=UserBacklog.BacklogType.event_worksheet,
            description='您有一条事件工单待处理'

        )


class AlarmEventWorkSheetListSerializer(CustomModelSerializer):
    """事件工单列表序列化器"""
    event_name = serializers.CharField(source='alarm_event.event_name', required=False)
    event_code = serializers.CharField(source='alarm_event.event_code', required=False)
    event_state = serializers.CharField(source='alarm_event.event_state', required=False)
    priority = serializers.CharField(source='alarm_event.priority', required=False)
    event_type = serializers.CharField(source='alarm_event.event_type', required=False)
    dispose_user_name = serializers.CharField(label='处置人名称', source='dispose_user.username', required=False)
    dispose_user_id = serializers.IntegerField(label='处置人ID', source='dispose_user.id', required=False)
    event_id = serializers.IntegerField(source='alarm_event.id', read_only=True)
    start_time = serializers.DateTimeField(label='开始时间', required=False)
    end_time = serializers.DateTimeField(label='结束时间', required=False)

    class Meta:
        model = EventWorkSheet
        fields = (
            'event_work_sheet_id', 'work_sheet_code', 'sheet_state', 'event_name', 'event_code',
            'event_id', 'start_time', 'end_time', 'priority', 'event_type', 'event_state', 'dispose_user_id',
            'dispose_user_name', 'close_user', 'close_time', 'close_opinion'
        )

        extra_kwargs = {
            'work_sheet_code': {
                'required': False,
                'validators': []
            },
            'event_name': {
                'allow_blank': True
            },
            'sheet_state': {
                'required': False,
            },
            'event_work_sheet_id': {
                'read_only': True,
                'source': 'id'
            },
            # 'dispose_user_id': {
            #     # 'read_only': True,
            #     'source': 'dispose_user'
            # }
        }

    def validate_event_type(self, event_type):
        """event_type参数校验"""
        event_type_list = ['1', '2']
        if event_type not in event_type_list:
            self.param_error(param_name='event_type')

        return event_type

    def validate_priority(self, priority):
        """priority参数校验"""
        priority_list = ['1', '2', '3', '4']
        if priority not in priority_list:
            self.param_error(param_name='priority')

        return priority

    def validate_event_state(self, event_state):
        """event_state参数校验"""
        event_state_list = DeviceAlarmEvent.EventState.values + PersonAlarmEvent.EventState.values
        if event_state not in event_state_list:
            self.param_error(param_name='event_state')

        return event_state

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                value = ''

            if key.find('close_time') != -1:
                data[key] = str(value).replace('T', ' ').split('.')[0]

        return data


class AlarmEventWorkSheetCloseSerializer(CustomModelSerializer):
    """自动上报事件工单销单序列化器"""

    class Meta:
        model = EventWorkSheet
        fields = (
            'sheet_state', 'close_user', 'close_time', 'close_opinion'
        )

        extra_kwargs = {
            'sheet_state': {
                'read_only': True,
            },
        }

    def update(self, instance, validated_data):
        """自动上报事件工单误派销单"""
        event_state = instance.alarm_event.event_state
        # 事件状态校验
        self.check_event_state(event_state)

        instance = super().update(instance, validated_data)

        return instance

    def check_event_state(self, event_state):
        """确认误派单状态为待处置"""
        if event_state != DeviceAlarmEvent.EventState.UNDISPOSED:
            self.param_error(param_name=event_state, code=ErrorType.EVENT_STATE)

    def validate(self, attrs):
        """
        参数校验
        """
        close_opinion = attrs.get('close_opinion')

        if not close_opinion:
            self.param_error(param_name='close_opinion', code=ErrorType.NULL)

        attrs['close_user'] = self.context["request"].user.username
        attrs['close_time'] = datetime.datetime.now()
        attrs['sheet_state'] = EventWorkSheet.SheetState.CLOSED

        return attrs


class DeployAlarmSerializer(CustomModelSerializer):
    """布控报警序列化器"""

    alarm_time = serializers.CharField(source='event.alarm_time')
    resource_name = CustomCharField(source='resource.name')
    resource_type = CustomCharField(source='resource.resource_type')

    class Meta:
        model = DeployAlarmRecord
        fields = [
            'event_id', 'person_db_image_url', 'alarm_image_url', 'score', 'name', 'type', 'number', 'country',
            'city', 'db_name', 'monitor_type', 'db_type', 'level', 'customType', 'alarm_time', 'sex',
            'resource_name', 'resource_id', 'resource_type',
        ]


class DeploySnapSerializer(CustomModelSerializer):
    """布控抓拍序列化器"""

    resource_id = serializers.IntegerField(source='camera.resource_id')
    resource_name = CustomCharField(source='camera.resource.name')
    resource_type = CustomCharField(source='camera.resource.resource_type')

    class Meta:
        model = DeployPersonSnapRecord
        fields = ['snap_image_url', 'snap_time', 'resource_name', 'resource_type', 'resource_id']


class PlacementAlarmSerializer(CustomModelSerializer):
    """机位报警信息"""

    event_name = serializers.DateTimeField(source='event.event_name')
    alarm_time = serializers.DateTimeField(source='event.alarm_time')
    resource_name = CustomCharField(source='resource.name')
    resource_type = CustomCharField(source='resource.resource_type')

    class Meta:
        model = PlaceAlarmRecord
        fields = ['event_id', 'event_name', 'alarm_time', 'resource_name', 'resource_id', 'resource_type']
        extra_kwargs = {'event_id': {'source': 'id'}}


class PlacementSafeguardSerializer(CustomModelSerializer):
    """机位保障信息"""

    flight_number = CustomCharField(source='flight.flight_number')
    resource_name = CustomCharField(source='camera.resource.name')
    resource_id = serializers.IntegerField(source='camera.resource_id')
    resource_type = CustomCharField(source='camera.resource.resource_type')

    class Meta:
        model = PlaceSafeguardRecord
        fields = [
            'resource_id', 'resource_name', 'resource_type', 'safeguard_name', 'safeguard_time',
            'safeguard_image_url', 'flight_number'
        ]


class ScopesAlarmSerializer(CustomModelSerializer):
    """围界报警信息序列化器"""

    device_name = serializers.CharField(source='device.device_name')
    device_code = serializers.CharField(source='device.device_code')

    class Meta:
        model = DeviceAlarmEvent
        fields = [
            'event_id', 'event_name', 'device_name', 'device_code',
            'alarm_time', 'area_code', 'priority'
        ]
        extra_kwargs = {'event_id': {'source': 'id'}}


class MonitorScopesAlarmSerializer(CustomModelSerializer):
    """围界WebApi报警信息序列化器"""

    device_name = serializers.CharField(source='device.device_name')
    device_code = serializers.CharField(source='device.device_code')
    flow_address = serializers.CharField(source='device.cameradevice.flow_address')

    class Meta:
        model = DeviceAlarmEvent
        fields = [
            'event_id', 'event_name', 'device_name', 'device_code',
            'alarm_time', 'area_code', 'priority', 'flow_address'
        ]
        extra_kwargs = {'event_id': {'source': 'id'}}


class DensityAlarmSerializer(CustomModelSerializer):
    """密度报警"""

    alarm_time = serializers.DateTimeField(source='event.alarm_time')
    priority = serializers.IntegerField(source='event.priority')
    device_name = serializers.CharField(source='event.device.device_name')
    device_code = serializers.CharField(source='event.device.device_code')
    flow_address = serializers.CharField(source='event.device.cameradevice.flow_address')

    class Meta:
        model = PersonDensityRecord
        fields = [
            'alarm_image_url', 'alarm_time', 'event_id', 'priority',
            'device_name', 'device_code', 'flow_address', 'total_people_number'
        ]
        extra_kwargs = {'event_id': {'source': 'event'}}


class PostureAlarmSerializer(CustomModelSerializer):
    """姿态动作报警"""

    alarm_time = serializers.DateTimeField(source='event.alarm_time')
    event_name = serializers.CharField(source='event.event_name')
    resource_name = CustomCharField(source='resource.name')
    resource_type = CustomCharField(source='resource.resource_type')

    class Meta:
        model = BehaviorAlarmRecord
        fields = [
            'alarm_image_url', 'event_name', 'resource_name', 'alarm_time',
            'event_id', 'resource_id', 'resource_type'
        ]
        extra_kwargs = {'event_id': {'source': 'event'}}
