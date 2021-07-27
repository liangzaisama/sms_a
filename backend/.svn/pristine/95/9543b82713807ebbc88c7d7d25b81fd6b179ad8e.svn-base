"""安保运行管理序列化器"""
from rest_framework import serializers

from operations.models import WatchAddressBook, EntranceAccessRecords, PlanInfo, StaffInfo
from users.models import UserDiary, Department
from security_platform import RET, ErrorType
from security_platform.utils.serializer import CustomModelSerializer


class WatchAddressBookSerializer(CustomModelSerializer):
    """值班通讯录列表序列化器"""

    class Meta:
        model = WatchAddressBook
        fields = ('department_name', 'staff_name', 'contact_mobile', 'duty_date')
        extra_kwargs = {
            'staff_name': {
                'allow_blank': True,
                'required': False
            },
            'department_name': {
                'required': False
            },
            'contact_mobile': {
                # 'read_only': True,
            },
            'duty_date': {
                'required': False

            },
        }


class EntranceAccessRecordsSerializer(CustomModelSerializer):
    """门禁通行记录列表序列化器"""
    start_time = serializers.DateTimeField(label='开始时间', required=False)
    end_time = serializers.DateTimeField(label='结束时间', required=False)

    class Meta:
        model = EntranceAccessRecords
        fields = ('device_code', 'record_time', 'card_no', 'holder', 'code_name', 'in_out', 'region_id',
                  'device_name', 'start_time', 'end_time')
        extra_kwargs = {
            'holder': {
                'required': False
            },
            'card_no': {
                'required': False
            },
            'device_code': {
                'required': False
            },
            'device_name': {
                'required': False
            },
            'record_time': {
                'read_only': True
            },
            'in_out': {
                'read_only': True
            },
            'region_id': {
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
                value = ''

            if key.find('record_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0][11:-3]

        return data


class UserDiarySerializer(CustomModelSerializer):
    """用户日志序列化器"""
    start_time = serializers.DateTimeField(label='开始时间', required=False)
    end_time = serializers.DateTimeField(label='结束时间', required=False)
    username = serializers.CharField(label='用户名', required=False)
    handover_username = serializers.CharField(label='交接用户名', required=False)
    department_id = serializers.IntegerField(label='部门ID', required=False)

    class Meta:
        model = UserDiary
        fields = ('diary_id', 'user', 'job_content', 'job_time', 'is_handover', 'handover_user',
                  'handover_content', 'start_time', 'end_time', 'username', 'department_id', 'handover_username',
                  'is_confirm')
        extra_kwargs = {
            'diary_id': {
                'source': 'id',
                'read_only': True
            },
            'handover_user': {
                'required': False
            },
            'user': {
                'required': False,
                'allow_null': True
            },
            'handover_content': {
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

            if key == 'user':
                data['username'] = instance.user.username if instance.user else ''
            elif key == 'handover_user':
                data['handover_username'] = instance.handover_user.username if instance.handover_user else ''
            elif key.find('job_time') != -1:
                data[key] = value.replace('T', ' ').split('.')[0]

        if all([data['username'], data['handover_username']]) and data['is_handover'] is False:
            # 未交接日志交接人和交接内容置空
            if data['username'] == data['handover_username']:
                data['handover_username'] = ''
                data['handover_content'] = ''

        return data

    def validate_department_id(self, department_id):
        """验证部门id"""
        if not Department.objects.filter(id=department_id).exists():
            self.param_error(code=ErrorType.DOES_NOT_EXIST, model_name='部门')

        return department_id

    def create(self, validated_data):
        """创建日志"""
        if not isinstance(self.context['request'].data, list):
            validated_data = self.validate_create(validated_data)
        return super().create(validated_data)

    def validate_create(self, validated_data):
        """验证参数"""
        handover_user = validated_data.get('handover_user')
        handover_content = validated_data.get('handover_content')
        job_content = validated_data.get('job_content')
        is_handover = validated_data.get('is_handover')
        validated_data['user'] = self.context['request'].user
        if is_handover is None:
            self.param_error(code=ErrorType.NULL, param_name='is_handover')
        if is_handover is True:
            if not handover_user:
                self.param_error(code=ErrorType.BLANK, param_name='handover_user')
            if not handover_content:
                self.param_error(code=ErrorType.BLANK, param_name='handover_content')
            if not self.context['request'].user.is_superuser:
                if handover_user.department != self.context['request'].user.department:
                    self.param_error(code=ErrorType.INVALID_CHOICE, param_name='handover_user')
            return validated_data
        validated_data['handover_user'] = self.context['request'].user
        if not handover_content:
            validated_data['handover_content'] = job_content
        return validated_data


class UserDiaryConfirmSerializer(CustomModelSerializer):
    """用户日志交接确认序列化器"""

    class Meta:
        model = UserDiary
        fields = ('is_confirm',)

    def update(self, instance, validated_data):
        """确认交接"""
        self.validate_instance(instance)
        instance = super().update(instance, validated_data)
        return instance

    def validate(self, attrs):
        """补充参数"""
        is_confirm = 1
        attrs['is_confirm'] = is_confirm
        return attrs

    def validate_instance(self, instance):
        """校验交接用户,当前用户与交接用户不符，则抛出外部异常
           校验当前日志确认状态，如果为已确认，则抛出外部异常
           校验当前日志交接状态，如果为未交接，则抛出外部异常
        """
        user = self.context['request'].user
        handover_user = instance.handover_user
        is_confirm = instance.is_confirm
        is_handover = instance.is_handover
        if is_handover is False:
            self.param_error(errmsg="当前日志未交接无需确认", errcode=RET.EXPARAMERR)
        if user != handover_user:
            self.param_error(errmsg="当前用户与交接用户不符", errcode=RET.EXPARAMERR)
        if is_confirm is True:
            self.param_error(errmsg="当前日志已确认交接", errcode=RET.EXPARAMERR)


class PlanInfoListSerializer(CustomModelSerializer):
    """预案信息列表序列化器"""

    class Meta:
        model = PlanInfo
        fields = ('plan_id', 'plan_name', 'plan_code', 'keywords', 'description', 'gis_field', 'gis_basic_info')
        extra_kwargs = {
            'plan_id': {
                'source': 'id',
                'read_only': True
            },
            'plan_name': {
                'required': False,
                'allow_blank': True
            },
            'plan_code': {
                'required': False,
                'allow_blank': True
            },
            'keywords': {
                'required': False,
                'allow_blank': True
            },
        }


class PlanInfoSerializer(CustomModelSerializer):
    """预案信息管理序列化器"""

    class Meta:
        model = PlanInfo
        fields = (
            'plan_id', 'plan_name', 'plan_code', 'keywords', 'description', 'gis_basic_info', 'gis_field', 'doc_file')
        extra_kwargs = {
            'plan_id': {
                'source': 'id',
                'read_only': True
            },
            'plan_code': {
                'read_only': True
            },
            'doc_file': {
                'write_only': True
            },
        }

    def create(self, validated_data):
        """生成预案编码"""
        plan_code = PlanInfo.generate_plan_code()
        validated_data['plan_code'] = plan_code

        return super().create(validated_data)

    def validate_doc_file(self, doc_file):
        """校验预案文件格式"""
        doc_name = doc_file.name
        # 文件名后缀
        doc_suffix = doc_name[-3:]

        if doc_suffix != 'pdf':
            self.param_error(errcode=RET.EXPARAMERR, errmsg='文件格式错误')

        return doc_file


class PlanInfoUpdateSerializer(CustomModelSerializer):
    """预案信息编辑序列化器"""

    class Meta:
        model = PlanInfo
        fields = (
            'plan_id', 'plan_name', 'plan_code', 'keywords', 'description', 'gis_basic_info', 'gis_field', 'doc_file')
        extra_kwargs = {
            'plan_id': {
                'source': 'id',
                'read_only': True
            },
            'plan_code': {
                'read_only': True
            },
            'doc_file': {
                'read_only': True
            },
        }

    # def validate_doc_file(self, doc_file):
    #     """校验预案文件格式"""
    #     doc_name = doc_file.name
    #     # 文件名后缀
    #     doc_suffix = doc_name[-3:]
    #
    #     if doc_suffix != 'pdf':
    #         self.param_error(errcode=RET.EXPARAMERR, errmsg='文件格式错误')
    #
    #     return doc_file

    def update(self, instance, validated_data):
        """预案编辑"""

        # # 删除已存在的文件
        # self.context['view'].remove_file(instance)

        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                # value = ''

            if key.find('doc_file') != -1:
                data['doc_file'] = instance.doc_file.name[10:] if self.instance.doc_file else ''

        return data


class StaffInfoListSerializer(CustomModelSerializer):
    """员工信息列表序列化器"""

    phone_number = serializers.CharField(max_length=20, required=False)
    department_name = serializers.CharField(source='department.department_name', read_only=True)

    class Meta:
        model = StaffInfo
        fields = ['staff_id', 'staff_name', 'department_id', 'department_name', 'phone_number', 'sex']
        extra_kwargs = {
            'staff_name': {
                'required': False
            },
            'department_id': {
                'required': False,
                'source': 'department'
            },
            'sex': {
                'required': False

            },
            'staff_id': {
                'read_only': True,
                'source': 'id'
            },
        }


class StaffInfoSerializer(CustomModelSerializer):
    """员工信息序列化器"""

    class Meta:
        model = StaffInfo
        fields = ['staff_id', 'staff_name', 'department_id', 'phone_number', 'sex', 'picture',
                  'birthday', 'entry_date', 'staff_type', 'gis_basic_info', 'gis_field', 'description']
        extra_kwargs = {

            'department_id': {
                'source': 'department',
                'required': True
            },
            'staff_id': {
                'read_only': True,
                'source': 'id'
            },

        }

    def validate_phone_number(self, phone_number):
        """电话号码格式校验，只能是数字"""
        if not phone_number.isdigit():
            self.param_error(code=ErrorType.INCORRECT_TYPE, param_name='phone_number')

        return phone_number

    def to_representation(self, instance):
        """返回消息处理"""
        data = super().to_representation(instance)

        for key in list(data.keys()):
            value = data[key]
            if value is None:
                data[key] = ''
                # value = ''

            if key.find('department_id') != -1:
                data['department_name'] = self.instance.department.department_name if self.instance.department else ''

        return data
