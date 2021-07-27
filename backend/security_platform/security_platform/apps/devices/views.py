"""设备资源管理模块api

包含设备运行状态监控、设备运行状态列表、设备维修记录、设备基础信息管理、设备地图点位相关接口
"""
from collections import OrderedDict

from six import BytesIO
from xlwt import Workbook
from django.db.models import Count, F
from django.db import connection
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import MethodNotAllowed


from devices.utils import request_vms
from devices import serializers
from devices.models import DeviceInfo, DeviceMaintenanceRecords, DeviceGroup, DeviceLabel, WorkSheet, CameraDevice
from devices.filter import (
    DeviceObjectPermissionsFilter, DeviceInfoListFilter, DeviceExcludeFilter,
    DeviceRelateObjectPermissionsFilter, DeviceGisRadiusFilter
)
from security_platform.utils.viewsets import CustomModelViewSet
from security_platform.utils.permisssions import DeviceObjectPermission
from security_platform.utils.views import (
    CustomGenericAPIView, ListCustomAPIView, CreateListCustomAPIView,
    RetrieveUpdateCustomAPIView, UpdateCustomAPIView
)


class DeviceCountView(DeviceObjectPermission, CustomGenericAPIView):
    """设备类型状态统计

    Class Attributes:
        user_device_id:用户可操作设备的id元祖默认为空
        device_type: 设备所属设备类型，根据设备类型的枚举类定义，用于获取设备类型字段
        device_state: 设备所属设备状态，根据设备状态的枚举类定义，用于获取设备状态类型字段
    """

    filter_backends = (DeviceObjectPermissionsFilter,)

    device_state = 'device_state'
    device_type = 'device_type'
    count = 'count'
    device_state_count = 'device_state_count'
    user_device_id = ()

    def get_state_count(self, device_type_info):
        """获取每个设备类型对应状态数量数据"""

        with connection.cursor() as cursor:
            if len(self.user_device_id) > 1:
                sql = 'select {0}, count(id) from tb_device_info where id in {1} and device_type = "{2}"' \
                      ' group by {0}'.format(self.device_state, self.user_device_id, device_type_info)
            elif len(self.user_device_id) == 1:
                sql = 'select {0}, count(id) from tb_device_info where id = {1} and device_type = "{2}"' \
                      ' group by {0}'.format(self.device_state, self.user_device_id[0], device_type_info)
            else:
                sql = 'select {0}, count(id) from tb_device_info where id = 0 and device_type = "{2}"' \
                      ' group by {0}'.format(self.device_state, self.user_device_id, device_type_info)
            cursor.execute(sql)
            query_data = cursor.fetchall()

            return query_data

    def get_type_count(self):
        """获取每个设备类型对应的设备数量"""

        with connection.cursor() as cursor:
            if len(self.user_device_id) > 1:
                sql = 'select {0}, count(id) from tb_device_info where id in {1} group by {0}'.format(
                    self.device_type, self.user_device_id)
            if len(self.user_device_id) == 1:
                sql = 'select {0}, count(id) from tb_device_info where id = {1} group by {0}'.format(
                    self.device_type, self.user_device_id[0])
            # else:
            #     sql = 'select {0}, count(id) from tb_device_info where id = 0 group by {0}'.format(
            #         self.device_type, self.user_device_id)
            cursor.execute(sql)
            total_count_data = cursor.fetchall()

            return total_count_data

    def get_user_devices_id(self):
        """过滤用户可管理的设备 构造id元祖"""

        queryset = self.filter_queryset(DeviceInfo.objects.only('id').all())
        user_device_id = tuple(queryset.values_list('id', flat=True))

        self.user_device_id = user_device_id

        return user_device_id

    def get_state_data(self, state_count):
        """构造设备状态对象数据结构"""

        count_list = []
        state_list = []
        for count_info in state_count:
            # 构造查询数据
            count_dict = OrderedDict()
            count_dict[self.device_state] = count_info[0]
            count_dict[self.count] = count_info[1]
            count_list.append(count_dict)
            state_list.append(count_info[0])

        for device_state in DeviceInfo.DeviceState:
            # 构造默认数据
            state_dict = OrderedDict()
            state_dict[self.device_state] = device_state
            state_dict[self.count] = 0

            # 补全数据
            if device_state not in state_list:
                count_list.append(state_dict)

        return count_list

    def get_response_data(self, total_count_data):
        """构造整体返回数据结构"""
        count_list = []
        type_list = []
        for count_info in total_count_data:
            # 构造查询数据
            count_dict = OrderedDict()
            count_dict[self.device_type] = count_info[0]
            count_dict[self.count] = count_info[1]
            count_dict[self.device_state_count] = self.get_state_data(self.get_state_count(count_info[0]))
            count_list.append(count_dict)
            type_list.append(count_info[0])

        for device_type in DeviceInfo.DeviceType:
            # 构造默认数据
            type_dict = OrderedDict()
            type_dict[self.device_type] = device_type
            type_dict[self.count] = 0
            type_dict[self.device_state_count] = self.get_state_data(self.get_state_count(device_type))
            # 补全数据
            if device_type not in type_list:
                count_list.append(type_dict)

        return count_list

    def get(self, _):
        """获取设备类型状态统计信息"""
        # receive_logger.info("订阅主题:[('vms/#', 1)]")
        if self.get_user_devices_id():
            total_count_data = self.get_type_count()
        else:
            total_count_data = self.get_user_devices_id()
        # 构造数据
        data_list = self.get_response_data(total_count_data)

        return self.success_response(data=data_list)


class DeviceTypePercentageCountView(DeviceObjectPermission, CustomGenericAPIView):
    """设备类型百分比统计

    Class Attributes:
        user_device_id:用户可操作设备的id元祖默认为空
        device_type: 设备所属设备类型，根据设备类型的枚举类定义，用于获取设备类型字段
        device_state: 设备所属设备状态，根据设备状态的枚举类定义，用于获取设备状态类型字段
    """

    good_device_state_list = ("normal", "trouble_off")
    device_type = 'device_type'
    count = 'count'
    good_count = 'good_count'
    user_device_id = ()

    def get_type_count(self):
        """获取每个设备类型对应的设备数量"""

        with connection.cursor() as cursor:
            if len(self.user_device_id) > 1:
                sql = 'select {0}, count(id) from tb_device_info  group by {0}'.format(
                    self.device_type, self.user_device_id)
            elif len(self.user_device_id) == 1:
                sql = 'select {0}, count(id) from tb_device_info where id = {1} group by {0}'.format(
                    self.device_type, self.user_device_id[0])
            else:
                sql = 'select {0}, count(id) from tb_device_info where id = 0 group by {0}'.format(
                    self.device_type, self.user_device_id)
            cursor.execute(sql)
            total_count_data = cursor.fetchall()

            return total_count_data

    def get_type_trouble_count(self, device_type):
        """获取每个设备类型对应完好设备数量"""

        with connection.cursor() as cursor:
            # if len(self.user_device_id) > 1:
            sql = 'select {0}, count(id) from tb_device_info where device_type = "{2}" and device_state in {1}  ' \
                  'group by {0}'.format(self.device_type, self.good_device_state_list, device_type)
            # elif len(self.user_device_id) == 1:
            #     sql = 'select {0}, count(id) from tb_device_info where id = {1} group by {0}'.format(
            #         self.device_type, self.user_device_id[0])
            # else:
            #     sql = 'select {0}, count(id) from tb_device_info where id = 0 group by {0}'.format(
            #         self.device_type, self.user_device_id)
            cursor.execute(sql)
            total_count_data = cursor.fetchall()

            return total_count_data

    def get_user_devices_id(self):
        """获取所有的设备 构造id元祖"""

        queryset = self.filter_queryset(DeviceInfo.objects.only('id').all())
        user_device_id = tuple(queryset.values_list('id', flat=True))

        self.user_device_id = user_device_id

        return user_device_id

    @staticmethod
    def get_good_count(good_type_data):
        """获取对应设备类型完好设备数量"""
        if good_type_data:
            good_count = good_type_data[0][1]
        else:
            good_count = 0

        return good_count

    @staticmethod
    def structure_percentage_data(data_list):
        """构造百分比数据返回"""
        for count_info in data_list:
            if count_info['count'] == 0:
                count_info['percentage'] = "0.0%"
            else:
                percentage = (count_info['good_count'] / count_info['count']) * 100
                count_info['percentage'] = '{0}%'.format(round(percentage, 3))

        return data_list

    def get_response_data(self, total_count_data):
        """构造整体返回数据结构"""
        count_list = []
        type_list = []
        for count_info in total_count_data:
            # 构造查询数据
            count_dict = OrderedDict()
            count_dict[self.device_type] = count_info[0]
            count_dict[self.count] = count_info[1]
            count_dict[self.good_count] = self.get_good_count(self.get_type_trouble_count(count_info[0]))
            count_list.append(count_dict)
            type_list.append(count_info[0])

        for device_type in DeviceInfo.DeviceType:
            # 构造默认数据
            type_dict = OrderedDict()
            type_dict[self.device_type] = device_type
            type_dict[self.count] = 0
            type_dict[self.good_count] = 0
            # 补全数据
            if device_type not in type_list:
                count_list.append(type_dict)

        return self.complement_response_data(count_list)

    def complement_response_data(self, data_list):
        """补全数据"""
        # 获取设备总数量、总完好数量
        total_count_data = DeviceInfo.objects.all().aggregate(Count("id"))
        total_good_count_data = DeviceInfo.objects.filter(device_state__in=self.good_device_state_list).aggregate(
            Count("id"))

        # 构造数据
        total_count_dict = OrderedDict()
        total_count_dict['total_count'] = total_count_data['id__count']
        total_count_dict['total_good_count'] = total_good_count_data['id__count']
        percentage = (total_count_dict['total_good_count'] / total_count_dict['total_count']) * 100
        total_count_dict['percentage'] = '{0}%'.format(round(percentage, 3))

        data_list = self.structure_percentage_data(data_list)

        data = OrderedDict()
        data['category'] = data_list
        data['total'] = total_count_dict

        return data

    def get(self, _):
        """获取设备类型状态统计信息"""
        if self.get_user_devices_id():
            total_count_data = self.get_type_count()
        else:
            total_count_data = self.get_user_devices_id()
        # 构造数据
        data_list = self.get_response_data(total_count_data)

        return self.success_response(data=data_list)


class DeviceInfoView(ListCustomAPIView):
    """设备列表接口"""

    validate_data = None
    ordering = ['-id']
    ordering_fields = ['id']
    queryset = DeviceInfo.objects.all()
    filter_backends = (
        # 设备权限过滤
        DeviceObjectPermissionsFilter,
        # 排除参数,
        DeviceExcludeFilter,
        # url参数过滤
        DeviceInfoListFilter,
        # 排序
        OrderingFilter
    )

    def get_serializer_class(self):
        """根据场景值返回对应的序列化器类"""
        if self.validate_data is None:
            return serializers.DeviceQueryParamSerializer
        elif self.validate_data['scene'] == DeviceInfo.Scene.STATUS:
            return serializers.DeviceStatusSerializer
        elif self.validate_data['scene'] == DeviceInfo.Scene.INFO:
            return serializers.DeviceInfoSerializer

        return serializers.DeviceBasicSerializer

    def get_queryset(self):
        """根据场景值返回对应的序列化器类"""
        queryset = super().get_queryset()
        query_fields = ['id', 'device_name', 'device_type', 'device_code', 'area_code', 'ipv4']

        if self.validate_data['scene'] == DeviceInfo.Scene.STATUS:
            query_fields += ['device_state', 'maintenance']
        elif self.validate_data['scene'] == DeviceInfo.Scene.INFO:
            query_fields += ['port', 'switches']

        return queryset.only(*query_fields).prefetch_related('worksheet_set')

    def get(self, request, *args, **kwargs):
        """获取设备列表"""

        # 校验查询参数
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.validate_data = serializer.validated_data

        return super().get(request, *args, **kwargs)


class DeviceMaintenanceRecordsViewSet(CustomModelViewSet):
    """设备维修记录"""

    serializer_class = serializers.DeviceMaintenanceRecordsSerializer
    queryset = DeviceMaintenanceRecords.objects.only('id').all().order_by('-id')
    filter_backends = (DeviceRelateObjectPermissionsFilter,)

    def __init__(self, **kwargs):
        self.filter_data = OrderedDict()
        self._data = None
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data

            if 'device_name' in filter_data:
                filter_data['device_info__device_name__contains'] = filter_data['device_name']
                filter_data.pop('device_name')

            if 'device_code' in filter_data:
                filter_data['device_info__device_code__contains'] = filter_data['device_code']
                filter_data.pop('device_code')
            if 'operate_person' in filter_data:
                filter_data['operate_person__contains'] = filter_data['operate_person']
                filter_data.pop('operate_person')

            queryset = queryset.filter(**filter_data)

        return super().filter_queryset(queryset)

    # def get_serializer_context(self):
    #     """
    #     Extra context provided to the serializer class.
    #     """
    #     return {
    #         # 'request': self.request,  # 返回了self.request
    #         'format': self.format_kwarg,
    #         'view': self
    #     }

    def list(self, request, *args, **kwargs):
        """获取设备维修记录列表"""

        # 验证查询参数
        self.serializer_class = serializers.DeviceMaintenanceRecordsListSerializer
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)

        self.filter_data = serializer.validated_data
        return super().list(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def exports(self, request):
        """导出设备维修记录列表"""
        list_response = self.list(request)

        data = list_response.data['objects']
        if not data:
            return self.structure_empty_excel_data()

        self._data = data
        work_book = self.structure_excel_data()
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('device_maintenance_records.xls')
        response.write(sio.getvalue())

        return response

    def structure_excel_data(self):
        """构造excel数据"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'设备维修记录')
        work_book_data.write(0, 0, '设备名')
        work_book_data.write(0, 1, u'设备编码')
        work_book_data.write(0, 2, u'维修时间')
        work_book_data.write(0, 3, u'维修人员')
        work_book_data.write(0, 4, u'维修记录')
        work_book_data.write(0, 5, u'备注')
        work_book_data.write(0, 6, u'设备故障信息')
        work_book_data.write(0, 7, u'是否更换设备')
        # 写入数据
        excel_row = 1
        for maintenance_record_info in self._data:
            device_name = maintenance_record_info['device_name']
            device_code = maintenance_record_info['device_code']
            operate_time = maintenance_record_info['operate_time']
            operate_person = maintenance_record_info['operate_person']
            operate_records = maintenance_record_info['operate_records']
            note = maintenance_record_info['note']
            trouble_message = maintenance_record_info['trouble_message']
            is_change_device = maintenance_record_info['is_change_device']
            if is_change_device is False:
                is_change_device = '否'
            else:
                is_change_device = '是'
            work_book_data.write(excel_row, 0, device_name)
            work_book_data.write(excel_row, 1, device_code)
            work_book_data.write(excel_row, 2, operate_time)
            work_book_data.write(excel_row, 3, operate_person)
            work_book_data.write(excel_row, 4, operate_records)
            work_book_data.write(excel_row, 5, note)
            work_book_data.write(excel_row, 6, trouble_message)
            work_book_data.write(excel_row, 7, is_change_device)

            excel_row += 1

        # work_book.save("device_maintenance_records.xls")

        return work_book

    @staticmethod
    def structure_empty_excel_data():
        """构造excel数据模板"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'设备维修记录')
        work_book_data.write(0, 0, '设备名')
        work_book_data.write(0, 1, u'设备编码')
        work_book_data.write(0, 2, u'维修时间')
        work_book_data.write(0, 3, u'维修人员')
        work_book_data.write(0, 4, u'维修记录')
        work_book_data.write(0, 5, u'备注')
        work_book_data.write(0, 6, u'设备故障信息')
        work_book_data.write(0, 7, u'是否更换设备')
        # work_book.save("device_maintenance_records.xls")
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('device_maintenance_records.xls')
        response.write(sio.getvalue())

        return response

    def update(self, request, *args, **kwargs):
        """禁止PUT请求修改维修记录"""
        raise MethodNotAllowed(self.request.method)

    def destroy(self, request, *args, **kwargs):
        """禁止DELETE请求删除维修记录"""
        raise MethodNotAllowed(self.request.method)


class DeviceBasicsViewSet(DeviceObjectPermission, CustomModelViewSet):
    """设备基础信息"""
    serializer_class = serializers.DeviceBasicsSerializer
    filter_backends = (DeviceObjectPermissionsFilter,)
    queryset = DeviceInfo.objects.only('id').all()

    def retrieve(self, request, *args, **kwargs):
        """获取设备详情"""

        # 视频监控设备需要附加字段，返回视频监控设备的查询集和序列化器
        device = self.get_object()
        if device.device_type == DeviceInfo.DeviceType.CAMERA.value:
            self.serializer_class = serializers.CameraDeviceBasicsSerializer
            self.queryset = CameraDevice.objects.all()

        return super().retrieve(request, *args, **kwargs)

    @action(methods=['get'], detail=True)
    def owners(self, request, *args, **kwargs):
        """获取同部门拥有设备权限的普通用户信息"""
        device = self.get_object()

        user = request.user
        user_department = user.department

        owners_data = device.users.filter(department=user_department).values('username', user_id=F('id'))

        return self.success_response(data=list(owners_data))

    @action(methods=['patch'], detail=True)
    def details(self, request, *args, **kwargs):
        """修改额外增加字段信息"""
        self.serializer_class = serializers.DeviceExtraFieldsSerializer

        # 视频监控设备需要附加字段，返回视频监控设备的查询集和序列化器
        device = self.get_object()
        if device.device_type == DeviceInfo.DeviceType.CAMERA.value:
            self.serializer_class = serializers.CameraDeviceExtraFieldsSerializer
            self.queryset = CameraDevice.objects.all()

        return super().update(request, *args, **kwargs)

    @action(methods=['patch'], detail=True)
    def gis(self, request, *args, **kwargs):
        """修改点位信息"""
        self.serializer_class = serializers.DeviceGISSerializer
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """禁止POST请求创建设备"""
        raise MethodNotAllowed(self.request.method)

    def update(self, request, *args, **kwargs):
        """禁止PUT请求修改设备参数"""
        raise MethodNotAllowed(self.request.method)

    def destroy(self, request, *args, **kwargs):
        """禁止DELETE请求删除设备信息"""
        raise MethodNotAllowed(self.request.method)


class DeviceGroupsViewSet(CustomModelViewSet):
    """设备组信息"""
    serializer_class = serializers.DeviceGroupSerializer
    queryset = DeviceGroup.objects.only('id').all()

    def filter_queryset(self, queryset):
        """过滤用户创建的设备组信息"""

        user = self.request.user
        filter_data = OrderedDict()
        filter_data['user'] = user

        device_data = queryset.filter(**filter_data).order_by('id')

        return device_data

    def create(self, request, *args, **kwargs):
        """设备添加设备组"""
        self.request.data['user_id'] = self.request.user.id
        return super().create(request, *args, **kwargs)

    @action(methods=['patch'], detail=True)
    def detachments(self, request, *args, **kwargs):
        """从设备组中移除设备"""
        self.serializer_class = serializers.DeviceGroupDetachmentsSerializer
        return super().update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """禁止PUT请求修改设备组参数"""
        raise MethodNotAllowed(self.request.method)


class DeviceLabelsViewSet(CustomModelViewSet):
    """设备标签信息"""
    serializer_class = serializers.DeviceLabelSerializer
    queryset = DeviceLabel.objects.only('id').all()

    def filter_queryset(self, queryset):
        """过滤用户创建的标签信息"""

        user = self.request.user
        filter_data = OrderedDict()
        filter_data['user'] = user

        label_data = queryset.filter(**filter_data).order_by('id')

        return label_data

    def create(self, request, *args, **kwargs):
        """设备添加标签信息"""
        self.request.data['user_id'] = self.request.user.id
        return super().create(request, *args, **kwargs)

    @action(methods=['patch'], detail=True)
    def detachments(self, request, *args, **kwargs):
        """设备移除标签"""

        self.serializer_class = serializers.DeviceLabelDetachmentsSerializer
        return super().update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """禁止PUT请求修改设备标签参数"""
        raise MethodNotAllowed(self.request.method)


class WorkSheetView(CreateListCustomAPIView):
    """工单流程
    GET:工单列表
    POST:创建工单
    """
    serializer_class = serializers.WorkSheetCreateSerializer
    queryset = WorkSheet.objects.only('id').all().order_by('-id')
    filter_backends = (DeviceRelateObjectPermissionsFilter,)

    def __init__(self, **kwargs):
        self.filter_data = None
        self._data = None
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data

            if 'audit_user_name' in filter_data:
                filter_data['audit_user__username__contains'] = filter_data.pop('audit_user_name')
            if 'dispose_user_name' in filter_data:
                filter_data['dispose_user__username__contains'] = filter_data.pop('dispose_user_name')
            if 'device_name' in filter_data:
                filter_data['device_info__device_name__contains'] = filter_data.pop('device_name')
            if 'device_type' in filter_data:
                filter_data['device_info__device_type'] = filter_data.pop('device_type')
            if 'device_code' in filter_data:
                filter_data['device_info__device_code__contains'] = filter_data.pop('device_code')
            if filter_data.get('work_sheet_code'):
                filter_data['work_sheet_code__contains'] = filter_data.pop('work_sheet_code')

            queryset = queryset.filter(**filter_data)

        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        """根据请求方式返回对应的序列化器类"""
        if self.request.method == 'GET':
            return serializers.WorkSheetListSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        """
        工单列表
        """

        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.filter_data = serializer.validated_data
        return super().list(request, *args, **kwargs)
    # TODO 批量创建故障设备工单，由于不同设备权限所属用户不同，无法判断权限，暂时先不做，
    #  如果一定要有这方面需求，做成批量指派给当前登陆用户，绕过设备对应不同用户的权限判断
    # def post(self, request, *args, **kwargs):
    #     """单条创建"""
    #     if isinstance(request.data, dict):
    #         return super().post(request, *args, **kwargs)
    #     return self.bulk_create(request, *args, **kwargs)
    #
    # def bulk_create(self, request, *args, **kwargs):
    #     """批量创建"""
    #     if not request.data:
    #         self.param_error(errcode=RET.PARSEERR)
    #     serializer = self.get_serializer(data=request.data, many=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.validate_batch_serializer_data(serializer)
    #     self.perform_create(serializer)
    #
    #     headers = self.get_success_headers(serializer.data)
    #     return self.success_response(serializer.data, status_code=status.HTTP_201_CREATED, headers=headers)
    #
    # def validate_batch_serializer_data(self, serializer):
    #     """格式化之外的序列化校验"""
    #     user_list = [validated_data.get('dispose_user') for validated_data in
    #                  serializer.validated_data]
    #     device_list = [validated_data.get('device_info') for validated_data in
    #                    serializer.validated_data]
    #     # 如果指定了多个不同的用户则抛出内部异常
    #     if len(set(user_list)) > 1:
    #         self.param_error(param_name='dispose_user_id')
    #     # 如果指派用户不为当前登陆用户则抛出内部异常
    #     if user_list[0] != self.request.user:
    #         self.param_error(param_name='dispose_user_id')
    #     # 如果指定了多个相同的事件则抛出内部异常
    #     if len(set(device_list)) != len(device_list):
    #         self.param_error(param_name='device_id')
    #     return serializer.validated_data


class WorkSheetRetrieveView(RetrieveUpdateCustomAPIView):
    """工单详情
        GET:工单详情
        """
    serializer_class = serializers.WorkSheetListSerializer
    queryset = WorkSheet.objects.only('id').all()
    filter_backends = (DeviceRelateObjectPermissionsFilter,)

    def update(self, request, *args, **kwargs):
        """禁止PUT请求"""
        raise MethodNotAllowed(self.request.method)


class WorkSheetAuditView(UpdateCustomAPIView):
    """工单审核
    PUT:工单审核
    """
    serializer_class = serializers.WorkSheetAuditSerializer
    queryset = WorkSheet.objects.only('id').all()
    filter_backends = (DeviceRelateObjectPermissionsFilter,)


class WorkSheetCloseView(UpdateCustomAPIView):
    """工单查看关闭
    PUT:工单查看关闭
    """
    serializer_class = serializers.WorkSheetCloseSerializer
    queryset = WorkSheet.objects.only('id').all()
    filter_backends = (DeviceRelateObjectPermissionsFilter,)


class DeviceGisInfoView(ListCustomAPIView):
    """gis半径内的视频监控设备列表接口"""
    validate_data = None
    ordering = ['-id']
    ordering_fields = ['id']
    queryset = CameraDevice.objects.all()
    serializer_class = serializers.DeviceGisSerializer
    filter_backends = (
        # 设备权限过滤
        DeviceObjectPermissionsFilter,
        # 排序
        OrderingFilter,
        # gis半径过滤
        DeviceGisRadiusFilter
    )

    def get(self, request, *args, **kwargs):
        """获取设备列表"""
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.validate_data = serializer.validated_data

        return super().get(request, *args, **kwargs)


class DevicesScreenshotView(DeviceObjectPermission, CustomGenericAPIView):
    """摄像机屏幕截图"""

    queryset = DeviceInfo.objects.filter(device_type=DeviceInfo.DeviceType.CAMERA).only('device_code')

    def get(self, _, *args, **kwargs):
        """获取摄像机屏幕截图"""
        screenshot_url = f'vms/VideoSource/{self.get_object().device_code}/'
        return self.success_response(data={'screenshots': request_vms(screenshot_url, 'get', content_type='image')})
