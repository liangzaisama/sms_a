"""
设备资源管理模块序列化器
"""
from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser

from users.models import Department, User, UserBacklog
from devices.models import DeviceInfo, DeviceGroup, DeviceLabel, DeviceMaintenanceRecords, WorkSheet, CameraDevice
from security_platform import ErrorType, RET
from security_platform.utils.exceptions import PermissionsError
from security_platform.utils.permisssions import IsLeaderUser
from security_platform.utils.serializer import CustomModelSerializer


class DeviceBasicSerializer(CustomModelSerializer):
    """基础设备信息序列化"""

    class Meta:
        model = DeviceInfo
        fields = [
            'device_id', 'device_name', 'device_type', 'device_code',
            'area_code', 'gis_basic_info', 'gis_field', 'ipv4'
        ]
        extra_kwargs = {'device_id': {'source': 'id', 'read_only': True}}


class DeviceStatusSerializer(DeviceBasicSerializer):
    """设备状态设备信息序列化"""

    class Meta(DeviceBasicSerializer.Meta):
        fields = DeviceBasicSerializer.Meta.fields + ['device_state', 'maintenance', 'frequent_maintenance',
                                                      'device_cad_code']

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if key == 'device_state':
                if data[key] == DeviceInfo.DeviceState.TROUBLE_OPEN:
                    device_work_sheet_data = instance._prefetched_objects_cache.get('worksheet_set')
                    if device_work_sheet_data:
                        device_work_sheet = device_work_sheet_data.exclude(sheet_state=WorkSheet.
                                                                           SheetState.CLOSED)
                        data['device_work_sheet_id'] = device_work_sheet[0].id if device_work_sheet else ''
                        data['device_work_sheet_code'] = device_work_sheet[
                            0].work_sheet_code if device_work_sheet else ''
                    else:
                        data['device_work_sheet_id'] = ''
                        data['device_work_sheet_code'] = ''
                else:
                    data['device_work_sheet_id'] = ''
                    data['device_work_sheet_code'] = ''

        return data


class DeviceInfoSerializer(DeviceBasicSerializer):
    """设备状态完整信息序列化"""

    class Meta(DeviceBasicSerializer.Meta):
        fields = DeviceBasicSerializer.Meta.fields + ['ipv4', 'port', 'switches']


class DeviceQueryParamSerializer(DeviceBasicSerializer):
    """查询参数反序列化"""

    device_code = serializers.CharField(label='设备编码', max_length=200)
    scene = serializers.ChoiceField(choices=DeviceInfo.Scene.values)
    group_id = serializers.IntegerField(label='设备组ID')
    label_id = serializers.IntegerField(label='标签ID')
    exclude_department_id = serializers.IntegerField(label='部门id')
    exclude_user_id = serializers.IntegerField(label='用户id')

    class Meta(DeviceBasicSerializer.Meta):
        fields = DeviceBasicSerializer.Meta.fields + [
            'device_state',
            'scene',
            'group_id',
            'label_id',
            'exclude_department_id',
            'exclude_user_id',
            'ipv4'
        ]

    def check_permissions(self, has_permission):
        """判断是否拥有权限，无权限则报错"""
        if not has_permission:
            raise PermissionsError()

    def validate_exclude_department_id(self, exclude_department_id):
        """校验部门id"""
        if not Department.objects.filter(id=exclude_department_id).exists():
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name='部门')

        self.check_permissions(IsAdminUser().has_permission(self.context['request'], self.context['view']))

        return exclude_department_id

    def validate_exclude_user_id(self, exclude_user_id):
        """校验用户id"""
        try:
            user = User.objects.get(id=exclude_user_id)
        except User.DoesNotExist:
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name='用户')
        else:
            # 参数权限校验
            request = self.context['request']
            view = self.context['view']

            user_permission = IsLeaderUser()
            self.check_permissions(user_permission.has_permission(request, view))
            self.check_permissions(user_permission.has_object_permission(request, view, user))

        return exclude_user_id

    def validate_group_id(self, group_id):
        """校验设备组"""
        if not DeviceGroup.objects.filter(id=group_id, user=self.context['request'].user).exists():
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name='设备组')

        return group_id

    def validate_label_id(self, label_id):
        """校验设备标签"""
        if not DeviceLabel.objects.filter(id=label_id, user=self.context['request'].user).exists():
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name='设备标签')

        return label_id

    def validate(self, attrs):
        """其他参数校验"""
        if 'scene' not in attrs:
            self.param_error(code=ErrorType.REQUIRED, param_name='scene')

        return attrs


class DeviceLabelSerializer(CustomModelSerializer):
    """设备标签序列化器"""

    devices = serializers.ListField(label='设备组设备', write_only=True, child=serializers.IntegerField())

    class Meta:
        model = DeviceLabel
        fields = (
            'device_label_id', 'device_label_name', 'content', 'keywords', 'color', 'user_id', 'devices'
        )
        extra_kwargs = {
            'device_label_id': {
                'source': 'id'
            },
            'device_label_name': {
                'source': 'name'
            },
            'user_id': {
                'source': 'user',
                'required': False,
                'allow_null': True,
            },
        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if key == 'user_id':
                # 补充用户名字段
                data['username'] = instance.user.username if instance.user else ''

                if value != self.context["request"].user.id:
                    data.clear()

        return data

    def create(self, validated_data):
        """标签添加设备"""

        devices = validated_data.get('devices')

        if not devices:
            self.param_error(code=ErrorType.BLANK, param_name='devices')

        # 获取添加设备列表
        devices_data = DeviceInfo.objects.only('id').filter(id__in=devices)

        # 验证参数
        if len(devices) != devices_data.count():
            self.param_error(param_name='devices')

        # 验证设备是否属于用户
        for device_info in devices_data:
            if not device_info.is_belong_user(self.context["request"].user):
                self.param_error(code=ErrorType.ID_LIST, param_name='devices', field_name='设备ID')

        return super().create(validated_data)

    def validate_device_label_name(self, device_label_name):
        """校验标签名称重复"""
        if DeviceLabel.objects.filter(name=device_label_name, user=self.context["request"].user).exists():
            self.param_error(code=ErrorType.UNIQUE, param_name=device_label_name, errcode=RET.EXPARAMERR)

        return device_label_name


class DeviceLabelDetachmentsSerializer(CustomModelSerializer):
    """设备标签移除设备序列化器"""

    devices = serializers.ListField(label='设备组设备', write_only=True, child=serializers.IntegerField())

    class Meta:
        model = DeviceLabel
        fields = ('devices',)
        extra_kwargs = {
            'devices': {
                'required': True,
            },
        }

    def update(self, instance, validated_data):
        """标签移除设备"""

        devices = validated_data.get('devices')

        if not devices:
            self.param_error(code=ErrorType.BLANK, param_name='devices')

        # 获取移除设备列表
        devices_data = DeviceInfo.objects.only('id').filter(id__in=devices)
        label_devices = instance.devices.all()
        # 验证参数
        if len(devices) != devices_data.count():
            self.param_error(param_name='devices')

        # 验证设备是否属于用户
        for device_info in devices_data:
            if not device_info.is_belong_user(self.context["request"].user):
                self.param_error(code=ErrorType.ID_LIST, param_name='devices', field_name='设备ID')
            if device_info not in label_devices:
                self.param_error(errcode=RET.EXPARAMERR, code=ErrorType.ID_LIST_DEL,
                                 param_name=device_info.device_name, field_name=DeviceLabel._meta.verbose_name)

        # 移除设备列表
        instance.devices.remove(*devices_data)

        instance = super().update(instance, validated_data={})

        return instance


class DeviceGroupSerializer(CustomModelSerializer):
    """设备分组序列化器"""
    devices = serializers.ListField(label='设备组设备', write_only=True, child=serializers.IntegerField())

    class Meta:
        model = DeviceGroup
        fields = (
            'device_group_id', 'device_group_name', 'description', 'user_id', 'devices'
        )

        extra_kwargs = {
            'device_group_id': {
                'source': 'id',
            },
            'device_group_name': {
                'source': 'name'
            },
            'user_id': {
                'source': 'user',
                'required': False,
                'allow_null': True,
            },
        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if key == 'user_id':
                # 补充用户名字段
                data['username'] = instance.user.username if instance.user else ''

                if value != self.context["request"].user.id:
                    data.clear()

        return data

    def create(self, validated_data):
        """设备组添加设备"""

        devices = validated_data.get('devices')

        if not devices:
            self.param_error(code=ErrorType.BLANK, param_name='devices')

        # 获取添加设备列表
        devices_data = DeviceInfo.objects.only('id').filter(id__in=devices)

        # 验证参数
        if len(devices) != devices_data.count():
            self.param_error(param_name='devices')

        # 验证设备是否属于用户
        for device_info in devices_data:
            if not device_info.is_belong_user(self.context["request"].user):
                self.param_error(code=ErrorType.ID_LIST, param_name='devices', field_name='设备ID')
            # 验证设备组和设备是否一对一
            if DeviceGroup.objects.filter(user=self.context["request"].user, devices=device_info).exists():
                self.param_error(errcode=RET.EXPARAMERR, code=ErrorType.ID_LIST_ADD,
                                 param_name=device_info.device_name, field_name=DeviceGroup._meta.verbose_name)

        validated_data['user'] = self.context["request"].user

        return super().create(validated_data)

    def validate_device_group_name(self, device_group_name):
        """校验设备组名称重复"""
        if DeviceGroup.objects.filter(name=device_group_name, user=self.context["request"].user).exists():
            self.param_error(code=ErrorType.UNIQUE, param_name=device_group_name, errcode=RET.EXPARAMERR)

        return device_group_name


class DeviceGroupDetachmentsSerializer(CustomModelSerializer):
    """设备分组移除设备序列化器"""
    devices = serializers.ListField(label='设备组设备', write_only=True, child=serializers.IntegerField())

    class Meta:
        model = DeviceGroup
        fields = ('devices',)
        extra_kwargs = {
            'devices': {
                'required': True,
            },
        }

    def update(self, instance, validated_data):
        """设备组移除设备"""

        devices = validated_data.get('devices')

        if not devices:
            self.param_error(code=ErrorType.BLANK, param_name='devices')

        # 获取移除设备列表
        devices_data = DeviceInfo.objects.only('id').filter(id__in=devices)
        group_devices = instance.devices.all()
        # 验证参数
        if len(devices) != devices_data.count():
            self.param_error(param_name='devices')

        # 验证设备是否属于用户
        for device_info in devices_data:
            if not device_info.is_belong_user(self.context["request"].user):
                self.param_error(code=ErrorType.ID_LIST, param_name='devices', field_name='设备ID')
            if device_info not in group_devices:
                self.param_error(errcode=RET.EXPARAMERR, code=ErrorType.ID_LIST_DEL,
                                 param_name=device_info.device_name, field_name=DeviceGroup._meta.verbose_name)

        # 移除设备列表
        instance.devices.remove(*devices_data)

        instance = super().update(instance, validated_data={})

        return instance


class DeviceBasicsSerializer(CustomModelSerializer):
    """设备基础信息序列化器"""

    group_set = DeviceGroupSerializer(label='设备组列表', many=True, required=False)
    label_set = DeviceLabelSerializer(label='设备标签列表', many=True, required=False)

    class Meta:
        model = DeviceInfo
        fields = (
            'device_id', 'device_name', 'device_type', 'device_code', 'gis_field', 'switches', 'device_state',
            'ipv4', 'port', 'maintenance', 'area_code', 'frequent_maintenance', 'trouble_message', 'trouble_time',
            'installation_time', 'initial_image', 'service_life', 'group_set', 'label_set', 'gis_basic_info',
            'parent_id', 'device_cad_code'
        )

        extra_kwargs = {
            'device_id': {
                'source': 'id',
                'read_only': True
            },
            'device_name': {
                'allow_blank': True,
                'required': False
            },
            'device_code': {
                'allow_blank': True,
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

            if key == 'group_set':
                # 去除空值
                new_value = [group_info for group_info in value if group_info]
                data[key] = new_value

            if key == 'label_set':
                # 去除空值
                new_value = [label_info for label_info in value if label_info]
                data[key] = new_value
            if key == 'parent_id':
                data['parent_name'] = self.instance.parent.device_name if self.instance.parent else ''
                subs = self.instance.subs.all()
                if subs:
                    data['subs'] = [
                        {'sub_id': sub.id, 'sub_name': sub.device_name} for sub in subs
                    ]
                else:
                    data['subs'] = []

        return data


class CameraDeviceBasicsSerializer(CustomModelSerializer):
    """视频监控设备基础信息序列化器"""

    group_set = DeviceGroupSerializer(label='设备组列表', many=True, required=False)
    label_set = DeviceLabelSerializer(label='设备标签列表', many=True, required=False)

    class Meta:
        model = CameraDevice
        fields = (
            'device_id', 'device_name', 'device_type', 'device_code', 'gis_field', 'switches', 'device_state',
            'ipv4', 'port', 'maintenance', 'area_code', 'frequent_maintenance', 'trouble_message', 'trouble_time',
            'installation_time', 'initial_image', 'service_life', 'group_set', 'label_set', 'gis_basic_info',
            'parent_id', 'camera_type', 'device_cad_code', 'flow_address'
        )

        extra_kwargs = {
            'device_id': {
                'source': 'id',
                'read_only': True
            },
            'device_name': {
                'allow_blank': True,
                'required': False
            },
            'device_code': {
                'allow_blank': True,
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

            if key == 'group_set':
                # 去除空值
                new_value = [group_info for group_info in value if group_info]
                data[key] = new_value

            if key == 'label_set':
                # 去除空值
                new_value = [label_info for label_info in value if label_info]
                data[key] = new_value
            if key == 'parent_id':
                data['parent_name'] = self.instance.parent.device_name if self.instance.parent else ''
                subs = self.instance.subs.all()
                if subs:
                    data['subs'] = [
                        {'sub_id': sub.id, 'sub_name': sub.device_name} for sub in subs
                    ]
                else:
                    data['subs'] = []

        return data


class DeviceGISSerializer(CustomModelSerializer):
    """设备点位更新序列化器"""

    class Meta:
        model = DeviceInfo
        fields = ('gis_field', 'gis_basic_info')
        extra_kwargs = {
            'gis_field': {'required': True},
            'gis_basic_info': {'required': True},
        }


class DeviceExtraFieldsSerializer(CustomModelSerializer):
    """设备基础信息更新序列化器"""
    group_ids = serializers.ListField(label='设备组id列表', write_only=True, child=serializers.IntegerField())
    label_ids = serializers.ListField(label='设备标签id列表', write_only=True, child=serializers.IntegerField())

    class Meta:
        model = DeviceInfo
        fields = ('group_ids', 'label_ids', 'installation_time', 'initial_image', 'service_life', 'gis_basic_info',
                  'gis_field', 'device_cad_code')
        extra_kwargs = {'group_ids': {'required': True}, 'label_ids': {'required': True}}

    def validate_group_ids(self, group_ids):
        """校验设备组id列表"""

        update_group_queryset = DeviceGroup.objects.filter(id__in=group_ids)

        if len(group_ids) > 1:
            self.param_error(param_name='group_ids')

        if len(group_ids) != update_group_queryset.count():
            self.param_error(param_name='group_ids')

        for group in update_group_queryset:
            if group.user != self.context["request"].user:
                self.param_error(code=ErrorType.ID_LIST, param_name='group_ids', field_name='设备组ID')

        return group_ids

    def validate_label_ids(self, label_ids):
        """校验设备标签id列表"""

        device_label_queryset = DeviceLabel.objects.filter(id__in=label_ids)

        if len(label_ids) != device_label_queryset.count():
            self.param_error(param_name='label_ids')

        for label in device_label_queryset:
            if label.user != self.context["request"].user:
                self.param_error(code=ErrorType.ID_LIST, param_name='label_ids', field_name='标签ID')

        return label_ids

    # noinspection PyUnresolvedReferences
    def update(self, instance, validated_data):
        group_ids = validated_data.get('group_ids')
        label_ids = validated_data.get('label_ids')

        current_group = instance.group_set.all().filter(user=self.context["request"].user)
        current_label = instance.label_set.all().filter(user=self.context["request"].user)
        with transaction.atomic():
            # 更新设备组关系
            if current_group:
                instance.group_set.remove(*current_group)
            instance.group_set.add(*group_ids)

            # 更新设备标签关系
            if current_label:
                instance.label_set.remove(*current_label)
            instance.label_set.add(*label_ids)

        instance = super().update(instance, validated_data)

        return instance


class CameraDeviceExtraFieldsSerializer(CustomModelSerializer):
    """视频监控设备基础信息更新序列化器"""
    group_ids = serializers.ListField(label='设备组id列表', write_only=True, child=serializers.IntegerField())
    label_ids = serializers.ListField(label='设备标签id列表', write_only=True, child=serializers.IntegerField())

    class Meta:
        model = CameraDevice
        fields = ('group_ids', 'label_ids', 'installation_time', 'initial_image', 'service_life', 'gis_basic_info',
                  'gis_field', 'camera_type', 'device_cad_code')
        extra_kwargs = {'group_ids': {'required': True}, 'label_ids': {'required': True}}

    def validate_group_ids(self, group_ids):
        """校验设备组id列表"""

        update_group_queryset = DeviceGroup.objects.filter(id__in=group_ids)

        if len(group_ids) > 1:
            self.param_error(param_name='group_ids')

        if len(group_ids) != update_group_queryset.count():
            self.param_error(param_name='group_ids')

        for group in update_group_queryset:
            if group.user != self.context["request"].user:
                self.param_error(code=ErrorType.ID_LIST, param_name='group_ids', field_name='设备组ID')

        return group_ids

    def validate_label_ids(self, label_ids):
        """校验设备标签id列表"""

        device_label_queryset = DeviceLabel.objects.filter(id__in=label_ids)

        if len(label_ids) != device_label_queryset.count():
            self.param_error(param_name='label_ids')

        for label in device_label_queryset:
            if label.user != self.context["request"].user:
                self.param_error(code=ErrorType.ID_LIST, param_name='label_ids', field_name='标签ID')

        return label_ids

    def validate_camera_type(self, camera_type):
        """校验摄像机类型"""

        camera_type_list = CameraDevice.CameraType.labels
        if camera_type not in camera_type_list:
            self.param_error(param_name='camera_type', code=ErrorType.INVALID)

        return camera_type

    # noinspection PyUnresolvedReferences
    def update(self, instance, validated_data):
        group_ids = validated_data.get('group_ids')
        label_ids = validated_data.get('label_ids')

        current_group = instance.group_set.all().filter(user=self.context["request"].user)
        current_label = instance.label_set.all().filter(user=self.context["request"].user)
        with transaction.atomic():
            # 更新设备组关系
            if current_group:
                instance.group_set.remove(*current_group)
            instance.group_set.add(*group_ids)

            # 更新设备标签关系
            if current_label:
                instance.label_set.remove(*current_label)
            instance.label_set.add(*label_ids)

        instance = super().update(instance, validated_data)

        return instance


class DeviceMaintenanceRecordsSerializer(CustomModelSerializer):
    """设备设备维修记录序列化器"""

    class Meta:
        model = DeviceMaintenanceRecords
        fields = (
            'maintenance_record_id', 'device_id', 'is_change_device', 'operate_time', 'operate_person',
            'operate_records', 'note', 'image', 'audit_state', 'work_sheet_id'
        )

        extra_kwargs = {
            'maintenance_record_id': {
                'source': 'id',
            },
            'device_id': {
                'source': 'device_info',
            },
            'work_sheet_id': {
                'source': 'work_sheet',
                'required': False
            },
            'operate_person': {
                'read_only': True,
                'required': False
            },
            'audit_state': {
                'required': False,
                'read_only': True
            },
        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if key == 'device_id':
                # 补充设备相关字段
                data['device_name'] = instance.device_info.device_name if instance.device_info else ''
                data['device_code'] = instance.device_info.device_code if instance.device_info else ''
                data['trouble_message'] = instance.device_info.trouble_message if instance.device_info else ''

            if key == 'work_sheet_id':
                # 补充工单相关字段
                data['work_sheet_code'] = instance.work_sheet.work_sheet_code if instance.work_sheet else ''
                data['sheet_state'] = instance.work_sheet.sheet_state if instance.work_sheet else ''

            elif key.find('operate_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data

    def create(self, validated_data):
        """新增维修记录"""
        # 获取设备信息
        device_info = validated_data.get('device_info')

        # 获取设备对应工单，更新工单状态
        work_sheet = self.validate_work_sheet(device_info)
        work_sheet.sheet_state = WorkSheet.SheetState.DISPOSED
        work_sheet.save()

        # 维修记录添加工单信息、维修人信息
        validated_data['work_sheet'] = work_sheet
        validated_data['operate_person'] = work_sheet.dispose_user.username

        return super().create(validated_data)

    def validate_work_sheet(self, device_info):
        """校验维修设备对应工单状态"""

        # 获取维修人
        operate_person = self.context['request'].user

        work_sheet = WorkSheet.objects.filter(device_info=device_info,
                                              sheet_state=WorkSheet.SheetState.ASSIGNED).first()
        # 判断是否存在设备对应已指派带维修的状态的工单
        if not work_sheet:
            self.param_error(errmsg='设备{0}不存在已指派待维修的工单请重新选择设备'.format(device_info.device_name),
                             errcode=RET.EXPARAMERR)
        # 判断维修人与工单处置人是否相同
        if work_sheet.dispose_user != operate_person:
            self.param_error(errmsg='工单处置人与维修人不符', errcode=RET.EXPARAMERR)

        return work_sheet


class DeviceMaintenanceRecordsListSerializer(CustomModelSerializer):
    """设备设备维修记录列表序列化器"""
    device_name = serializers.CharField(label='设备名称只用于序列化', required=False)
    device_code = serializers.CharField(label='设备编码只用于序列化', required=False)

    class Meta:
        model = DeviceMaintenanceRecords
        fields = (
            'maintenance_record_id', 'device_id', 'is_change_device', 'operate_time', 'operate_person',
            'operate_records', 'note', 'image', 'device_name', 'device_code', 'audit_state', 'work_sheet_id'
        )

        extra_kwargs = {
            'maintenance_record_id': {
                'source': 'id',
            },
            'device_id': {
                'source': 'device_info',
            },
            'operate_person': {
                'allow_blank': True,
            },
            'work_sheet_id': {
                'source': 'work_sheet',
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

            if key == 'device_id':
                # 补充设备相关字段
                data['device_name'] = instance.device_info.device_name if instance.device_info else ''
                data['device_code'] = instance.device_info.device_code if instance.device_info else ''
                data['trouble_message'] = instance.device_info.trouble_message if instance.device_info else ''

            if key == 'work_sheet_id':
                # 补充工单相关字段
                data['work_sheet_code'] = instance.work_sheet.work_sheet_code if instance.work_sheet else ''
                data['sheet_state'] = instance.work_sheet.sheet_state if instance.work_sheet else ''

            elif key.find('operate_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        return data


class WorkSheetListSerializer(CustomModelSerializer):
    """工单流程列表序列化器"""
    device_name = serializers.CharField(label='设备名称', required=False)
    device_code = serializers.CharField(label='设备编码', required=False)
    device_type = serializers.CharField(label='设备类型', required=False)
    dispose_user_name = serializers.CharField(label='处置人名称', required=False)
    audit_user_name = serializers.CharField(label='审核人名称', required=False)

    class Meta:
        model = WorkSheet
        fields = (
            'work_sheet_id', 'device_id', 'dispose_user_id', 'device_name', 'device_code', 'device_type',
            'audit_user_id', 'audit_opinion', 'sheet_state', 'work_sheet_code', 'dispose_user_name', 'audit_user_name'
        )

        extra_kwargs = {
            'work_sheet_id': {
                'source': 'id',
                'read_only': True

            },
            'device_id': {
                'source': 'device_info',
                'required': False,
                'read_only': True
            },
            'work_sheet_code': {
                'required': False,
                'validators': []
            },
            'dispose_user_id': {
                'source': 'dispose_user',
                'required': False,
                'read_only': True
            },
            'audit_user_id': {
                'source': 'audit_user',
                'read_only': True
            },
            'audit_opinion': {
                'required': False,
                'read_only': True
            },

        }

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if key == 'device_id':
                # 补充设备相关字段
                data['device_name'] = instance.device_info.device_name if instance.device_info else ''
                data['device_code'] = instance.device_info.device_code if instance.device_info else ''
                data['device_type'] = instance.device_info.device_type if instance.device_info else ''
                data['trouble_message'] = instance.device_info.trouble_message if instance.device_info else ''
            elif key == 'dispose_user_id':
                # 补充设备相关字段
                data['dispose_user_name'] = instance.dispose_user.username if instance.dispose_user else ''
            elif key == 'audit_user_id':
                # 补充设备相关字段
                data['audit_user_name'] = instance.audit_user.username if instance.audit_user else ''
        return data


class WorkSheetCreateSerializer(CustomModelSerializer):
    """工单流程创建序列化器"""
    device_name = serializers.CharField(label='设备名称', required=False)
    device_code = serializers.CharField(label='设备编码', required=False)

    class Meta:
        model = WorkSheet
        fields = (
            'work_sheet_id', 'device_id', 'dispose_user_id', 'device_name', 'device_code', 'sheet_state',
            'work_sheet_code'
        )

        extra_kwargs = {
            'work_sheet_id': {
                'source': 'id',
                'read_only': True

            },
            'device_id': {
                'source': 'device_info',
            },
            'dispose_user_id': {
                'source': 'dispose_user',
            },
            'work_sheet_code': {
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

            if key == 'device_id':
                # 补充设备相关字段
                data['device_name'] = instance.device_info.device_name if instance.device_info else ''
                data['device_code'] = instance.device_info.device_code if instance.device_info else ''
                data['trouble_message'] = instance.device_info.trouble_message if instance.device_info else ''
            elif key == 'dispose_user_id':
                # 补充设备相关字段
                data['dispose_user_name'] = instance.dispose_user.username if instance.dispose_user else ''
        return data

    def create(self, validated_data):
        """创建工单"""
        # 控制数据库事务交易
        with transaction.atomic():
            # 生成工单编号
            work_sheet_code = WorkSheet.generate_work_sheet_code()
            validated_data['work_sheet_code'] = work_sheet_code

            # 生成工单
            instance = super().create(validated_data)
            # 生成用户代办事项
            self.create_user_back_log(instance)
        return instance

    def validate(self, attrs):
        """参数校验"""
        device_info = attrs.get('device_info')
        dispose_user = attrs.get('dispose_user')
        device_state = device_info.device_state
        user = self.context['request'].user

        # 校验指派人、处置人的设备权限
        device_info = self.validated_device_info_permission(user, dispose_user, device_info)

        # 查询设备对应是否有正在处理未关闭的工单
        work_sheet_data = WorkSheet.objects.filter(device_info=device_info).exclude(
            sheet_state=WorkSheet.SheetState.CLOSED)

        # 设备存在执行中的工单无法创建新工单
        if work_sheet_data:
            self.param_error(errmsg='设备{0}存在未关闭的工单请重新选择或处理'.format(device_info.device_name),
                             errcode=RET.EXPARAMERR)
        # 设备状态不为故障无法创建新工单
        if device_state != DeviceInfo.DeviceState.TROUBLE_OPEN:
            self.param_error(errmsg='设备{0}状态不为故障，无法创建工单'.format(device_info.device_name),
                             errcode=RET.EXPARAMERR)

        return attrs

    def validated_device_info_permission(self, user, dispose_user, device_info):
        """校验指派人、处置人的设备权限"""

        # 判断处置人设备权限
        if not device_info.is_belong_user(dispose_user):
            self.param_error(errmsg='处置人{0}不具有设备权限，请重新选择'.format(dispose_user.username),
                             errcode=RET.EXPARAMERR)
        # 判断指派人设备权限
        if not device_info.is_belong_user(user):
            self.param_error(errmsg='指派人{0}不具有设备权限，请重新选择'.format(user.username), errcode=RET.EXPARAMERR)

        return device_info

    def create_user_back_log(self, instance):
        """创建用户代办事项"""
        UserBacklog.objects.create(
            object_id=instance.id,
            user=instance.dispose_user,
            backlog_type=UserBacklog.BacklogType.device_worksheet,
            description='您有一条设备工单待处理'

        )


class WorkSheetAuditSerializer(CustomModelSerializer):
    """工单审核序列化器"""
    audit_state = serializers.CharField(label='审核状态', required=False)

    class Meta:
        model = WorkSheet
        fields = (
            'audit_user_id', 'audit_opinion', 'sheet_state', 'audit_state', 'dispose_user_id'
        )

        extra_kwargs = {
            'audit_user_id': {
                'required': False,
                'source': 'audit_user',

            },
            'dispose_user_id': {
                'required': False,
                'source': 'dispose_user',
                'allow_null': True
            },
            'audit_opinion': {
                'required': True,
                'allow_blank': False,
                'allow_null': False,
            },
            'sheet_state': {
                'required': False
            },

        }

    def update(self, instance, validated_data):
        """修改工单状态，同时更新维修记录审核状态"""
        audit_state = validated_data.get('audit_state')
        dispose_user = validated_data.get('dispose_user')
        instance = self.validate_sheet_state(instance)
        device_info = instance.device_info

        with transaction.atomic():
            # 修改工单状态,重新指派处置人则为已指派，否则为已审核
            if dispose_user:
                # 校验处置人设备权限
                self.validate_dispose_user_permission(dispose_user, device_info)
                instance.sheet_state = WorkSheet.SheetState.ASSIGNED
                # 同时更改用户代办事项
                user_backlog = UserBacklog.objects.filter(object_id=instance.id).first()
                if user_backlog:
                    user_backlog.user = dispose_user
                    user_backlog.save()

            else:
                instance.sheet_state = WorkSheet.SheetState.AUDITED

            # 获取工单对应设备维修记录
            device_maintenance_record = DeviceMaintenanceRecords.objects.filter(device_info=device_info,
                                                                                work_sheet=instance,
                                                                                audit_state=DeviceMaintenanceRecords.
                                                                                AuditState.UNAUDITED).first()
            if not device_maintenance_record:
                self.param_error(errmsg="工单对应待审核状态设备维修记录不存在请重新选择或处理", errcode=RET.EXPARAMERR)

            # 更新设备维修记录状态
            device_maintenance_record.audit_state = audit_state
            device_maintenance_record.save()

            del validated_data['audit_state']
        return super().update(instance, validated_data)

    def validate_sheet_state(self, instance):
        """工单状态校验"""
        # 获取当前工单状态
        sheet_state = instance.sheet_state
        # 可审核的工单状态为已处置
        if sheet_state != WorkSheet.SheetState.DISPOSED:
            self.param_error(errmsg="只有状态为已处置的工单才能审核", errcode=RET.EXPARAMERR)

        return instance

    def validate(self, attrs):
        """参数校验"""
        audit_state = attrs.get('audit_state')
        dispose_user = attrs.get('dispose_user')
        if audit_state is None:
            self.param_error(param_name='audit_state', code=ErrorType.NULL)
        # 获取审核后状态列表
        audit_state_list = DeviceMaintenanceRecords.AuditState.values[1:]

        # 审核后状态为已通过或未通过
        if audit_state not in audit_state_list:
            self.param_error(param_name='audit_state', code=ErrorType.INVALID)

        # 已通过审核的工单不可重新指派
        if audit_state == audit_state_list[0] and dispose_user:
            del attrs['dispose_user']
        # 未通过审核的工单指派人不能为空
        if audit_state == audit_state_list[1] and 'dispose_user' in attrs:
            if dispose_user is None:
                del attrs['dispose_user']

        attrs['audit_user'] = self.context['request'].user
        return attrs

    def validate_dispose_user_permission(self, dispose_user, device_info):
        """校验处置人权限"""
        if not device_info.is_belong_user(dispose_user):
            self.param_error(errmsg='处置人{0}不具有设备权限，请重新选择'.format(dispose_user.username),
                             errcode=RET.EXPARAMERR)

        return dispose_user

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
            if key == 'audit_user_id':
                # 补充设备相关字段
                data['audit_user_name'] = instance.audit_user.username if instance.audit_user else ''
            elif key == 'dispose_user_id':
                # 补充设备相关字段
                data['dispose_user_name'] = instance.dispose_user.username if instance.dispose_user else ''
        return data


class WorkSheetCloseSerializer(CustomModelSerializer):
    """工单关闭序列化器"""

    class Meta:
        model = WorkSheet
        fields = (
            'sheet_state',
        )

        extra_kwargs = {
            'sheet_state': {
                'required': False
            },
        }

    def update(self, instance, validated_data):
        """修改工单状态，同时更新设备状态"""

        instance = self.validate_sheet_state(instance)
        device_info = instance.device_info

        with transaction.atomic():
            # 修改工单状态
            instance.sheet_state = WorkSheet.SheetState.CLOSED

            # 更新设备状态
            device_state = device_info.device_state
            now_time = datetime.now()

            if device_state == DeviceInfo.DeviceState.TROUBLE_OFF:
                device_state = DeviceInfo.DeviceState.NORMAL

            device_info.device_state = device_state
            device_info.update_time = now_time
            device_info.maintenance += 1

            # 设备状态变更,设备维系记录加一
            device_info.save(update_fields=['device_state', 'update_time', 'maintenance'])

            # 删除工单对应代办事项
            user_backlog = UserBacklog.objects.filter(object_id=instance.id).first()
            if user_backlog:
                user_backlog.delete()

        return super().update(instance, validated_data)

    def validate_sheet_state(self, instance):
        """工单状态校验"""
        sheet_state = instance.sheet_state

        # 只有状态为已审核的工单才能关闭
        if sheet_state != WorkSheet.SheetState.AUDITED:
            self.param_error(errmsg="只有状态为已审核的工单才能关闭", errcode=RET.EXPARAMERR)

        return instance


class DeviceGisSerializer(CustomModelSerializer):
    """基础设备信息序列化"""

    class Meta:
        model = CameraDevice
        fields = [
            'device_id', 'flow_address', 'gis_field', 'cover_radius', 'gis_basic_info', 'device_code', 'device_name'
        ]
        extra_kwargs = {
            'device_id': {
                'source': 'id',
                'read_only': True
            },
            'cover_radius': {
                # 'write_only': True,
                'allow_null': False
            },
            'gis_field': {
                # 'write_only': True,
                'read_only': True
            },
            'device_code': {
                # 'write_only': True,
                'read_only': True
            },
            'device_name': {
                # 'write_only': True,
                'read_only': True
            },
        }

    def validate_gis_basic_info(self, gis_basic_info):
        """校验gis_basic_info格式"""
        if ',' not in gis_basic_info:
            self.param_error(param_name='gis_basic_info', code=ErrorType.INCORRECT_TYPE)

        correct_gis_basic_info = gis_basic_info.split(',')

        if len(correct_gis_basic_info) != 2:
            self.param_error(param_name='gis_basic_info', code=ErrorType.INCORRECT_TYPE)
        try:
            correct_gis_basic_info = [float(x) for x in correct_gis_basic_info]
        except ValueError:
            self.param_error(param_name='gis_basic_info', code=ErrorType.INCORRECT_TYPE)

        return correct_gis_basic_info

    def validate(self, attrs):
        """参数校验"""
        cover_radius = attrs.get('cover_radius')
        gis_field = attrs.get('gis_basic_info')

        if not cover_radius:
            self.param_error(param_name='cover_radius', code=ErrorType.NULL)
        if not gis_field:
            self.param_error(param_name='gis_basic_info', code=ErrorType.NULL)

        return attrs

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)
        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''

            if key == 'cover_radius':
                # 移除冗余字段字段
                del data['cover_radius']

        return data
