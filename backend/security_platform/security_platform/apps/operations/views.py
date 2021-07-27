"""
安保运行管理模块api
包含工作日志、值班通讯录、信息交互、预案管理、人力资源等接口
"""
import os
from collections import OrderedDict
from datetime import datetime

import xlrd
from six import BytesIO
from xlrd import XLDateError
from xlrd import xldate_as_tuple
from xlwt import Workbook
from rest_framework import mixins, status
from django.db import transaction
from django.http import HttpResponse, FileResponse
from django.utils.encoding import escape_uri_path
from django_redis import get_redis_connection

from users.models import UserDiary
from operations import serializers
from operations.models import WatchAddressBook, EntranceAccessRecords, PlanInfo, StaffInfo
from security_platform import logger
from security_platform import ErrorType, RET
from security_platform.utils.models import Convert
from security_platform.utils.views import (
    ListCustomAPIView, CustomGenericAPIView, CreateListCustomAPIView, RetrieveUpdateCustomAPIView
)


class WatchAddressBookView(ListCustomAPIView):
    """
    获取值班通讯录列表
    list: 获取值班通讯录列表
    """
    serializer_class = serializers.WatchAddressBookSerializer
    queryset = WatchAddressBook.objects.all().only('id')

    def __init__(self, **kwargs):
        self.filter_data = None
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data

            if 'staff_name' in filter_data:
                filter_data['staff_name__contains'] = filter_data.pop('staff_name')

            query_set = queryset.filter(**filter_data).order_by('-duty_date')
        else:
            query_set = super().filter_queryset(queryset).order_by('-duty_date')

        return query_set

    def get(self, request, *args, **kwargs):
        """值班通讯录列表"""
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)

        self.filter_data = serializer.validated_data
        return super().get(request, *args, **kwargs)


class WatchAddressUploadBookView(CustomGenericAPIView):
    """
   上传值班通讯录
   post: 上传值班通讯录
   """
    serializer_class = serializers.WatchAddressBookSerializer
    queryset = WatchAddressBook.objects.all().only('id')

    def __init__(self, **kwargs):
        self.repeated_count = 0
        self.no_repeated_count = 0
        self.empty_count = 0
        self.duty_list = []
        super().__init__(**kwargs)

    def post(self, request):
        """上传excel格式值班通讯录"""
        excel_data = request.FILES.get('excel')
        if not excel_data:
            self.param_error(param_name='excel', code=ErrorType.NULL)
        excel_type = excel_data.name.split('.')[1]
        if excel_type in ['xlsx', 'xls']:
            # 开始解析上传的excel表格,获取工作表
            work_book = xlrd.open_workbook(filename=None, file_contents=excel_data.read())

            table = work_book.sheets()[0]
            # 行数
            n_rows = table.nrows
            # 列数
            n_cols = table.ncols

            success_msg = self.structure_excel_data(table, n_rows, n_cols)
        else:
            logger.error('上传文件类型错误！')
            return self.error_response(errcode=RET.PARAMERR, errmsg='上传文件类型错误')

        return self.success_response(data=success_msg)

    def structure_excel_data(self, table, n_rows, n_cols):
        """构造数据"""
        # 控制数据库事务交易
        with transaction.atomic():
            for rows_index in range(1, n_rows):
                # 获取每行值
                row = table.row_values(rows_index)
                for cols_index in range(0, n_cols):
                    # 如果值为float则转换为int,避免出现1输出为1.0的情况
                    if type(row[cols_index]) == float:
                        row[cols_index] = int(row[cols_index])
                # 查看行值是否为空
                if row:
                    self.analysis_excel_data(row)
                else:
                    # 空行值计数
                    self.empty_count += 1
            success_msg = f'数据导入成功，共{n_rows - 1}条,成功{self.no_repeated_count}条，重复{self.repeated_count}条，' \
                          f'有{self.empty_count}条为空'
            logger.info(success_msg)
        if success_msg:
            return success_msg
        return self.error_response(errcode=RET.PARAMERR, errmsg='解析excel文件或者数据插入错误')

    def analysis_excel_data(self, row):
        """解析excel数据并保存"""
        duty_data = OrderedDict()
        duty_data['department_name'] = row[0]
        duty_data['staff_name'] = row[1]
        duty_data['contact_mobile'] = row[2]
        # xlrd读取xls文件时间整数值转换为date形式
        if isinstance(row[3], str):
            duty_date = row[3]
        else:
            try:
                duty_date = str(datetime(*xldate_as_tuple(row[3], 0)))[0:10]
            except XLDateError:
                return self.param_error(errcode=RET.PARAMERR, errmsg='日期格式解析错误')
        duty_data['duty_date'] = duty_date
        serializer = self.get_serializer(data=duty_data, partial=True)
        serializer.is_valid(raise_exception=True)
        # 判断该行值是否在数据库中重复
        if WatchAddressBook.objects.filter(**duty_data).exists():
            # 重复值计数
            self.repeated_count += 1
        else:
            # 非重复计数
            self.no_repeated_count += 1

            serializer.save()


class WatchAddressBookDownloadView(ListCustomAPIView):
    """
    下载值班通讯录
    list: 获取值班通讯录列表
    address_book_download: 下载值班通讯录列表
    """
    serializer_class = serializers.WatchAddressBookSerializer
    queryset = WatchAddressBook.objects.all().only('id')

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

            if 'staff_name' in filter_data:
                filter_data['staff_name__contains'] = filter_data.pop('staff_name')

            query_set = queryset.filter(**filter_data).order_by('-duty_date')
        else:
            query_set = super().filter_queryset(queryset).order_by('-duty_date')

        return query_set

    def get(self, request, *args, **kwargs):
        """值班通讯录列表"""
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)

        self.filter_data = serializer.validated_data
        response = super().get(request, *args, **kwargs)
        data = response.data
        if data.get('objects'):
            self._data = response.data['objects']
            return self.address_book_download()
        return self.download_empty_excel()

    def address_book_download(self):
        """下载值班通讯录"""
        work_book = self.structure_excel_data()
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('contact.xls')
        response.write(sio.getvalue())

        return response

    def structure_excel_data(self):
        """构造excel数据"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'值班通讯录')
        work_book_data.write(0, 0, u'部门名称')
        work_book_data.write(0, 1, u'值班人员')
        work_book_data.write(0, 2, u'联系电话')
        work_book_data.write(0, 3, u'值班日期')
        # 写入数据
        excel_row = 1
        for book_info in self._data:
            department_name = book_info['department_name']
            staff_name = book_info['staff_name']
            contact_mobile = book_info['contact_mobile']
            duty_date = book_info['duty_date']

            work_book_data.write(excel_row, 0, department_name)
            work_book_data.write(excel_row, 1, staff_name)
            work_book_data.write(excel_row, 2, contact_mobile)
            work_book_data.write(excel_row, 3, duty_date)

            excel_row += 1

        return work_book

    @staticmethod
    def download_empty_excel():
        """下载值班通讯录模板"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'值班通讯录')
        work_book_data.write(0, 0, u'部门名称')
        work_book_data.write(0, 1, u'值班人员')
        work_book_data.write(0, 2, u'联系电话')
        work_book_data.write(0, 3, u'值班日期')
        # work_book.save("contact.xls")
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('contact.xls')
        response.write(sio.getvalue())

        return response


class WatchAddressBookTemplateDownloadView(CustomGenericAPIView):
    """
    下载值班通讯录模板
    GET: 下载值班通讯录模板
    """
    serializer_class = serializers.WatchAddressBookSerializer
    queryset = WatchAddressBook.objects.all().only('id')

    def get(self, request, *args, **kwargs):
        """值班通讯录列表"""
        template_data = self.download_empty_excel()
        return template_data

    @staticmethod
    def download_empty_excel():
        """下载值班通讯录模板"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'值班通讯录')
        work_book_data.write(0, 0, u'部门名称')
        work_book_data.write(0, 1, u'值班人员')
        work_book_data.write(0, 2, u'联系电话')
        work_book_data.write(0, 3, u'值班日期')
        work_book_data.write(1, 0, 'AOC')
        work_book_data.write(1, 1, '张三')
        work_book_data.write(1, 2, '13812345678')
        work_book_data.write(1, 3, '2021-01-01')
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('contact.xls')
        response.write(sio.getvalue())

        return response


class AccessRecordsView(ListCustomAPIView):
    """
    获取门禁通行记录列表
    get: 获取门禁通行记录列表
    """
    serializer_class = serializers.EntranceAccessRecordsSerializer
    queryset = EntranceAccessRecords.objects.all().only('id')

    def __init__(self, **kwargs):
        self.filter_data = None
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data

            if 'holder' in filter_data:
                filter_data['holder__contains'] = filter_data.pop('holder')
            if 'device_name' in filter_data:
                filter_data['device_name__contains'] = filter_data.pop('device_name')
            if 'start_time' in filter_data:
                filter_data['record_time__gte'] = filter_data.pop('start_time')
            if 'end_time' in filter_data:
                filter_data['record_time__lte'] = filter_data.pop('end_time')

            query_set = queryset.filter(**filter_data).order_by('-record_time')
        else:
            query_set = super().filter_queryset(queryset).order_by('-record_time')

        return query_set

    def get(self, request, *args, **kwargs):
        """通行记录"""
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)

        self.filter_data = serializer.validated_data
        return super().get(request, *args, **kwargs)


class UserDiaryView(CreateListCustomAPIView):
    """获取、创建用户日志
        get:获取用户日志列表
        post:创建用户日志列表
    """
    serializer_class = serializers.UserDiarySerializer
    queryset = UserDiary.objects.all().only('id')

    def __init__(self, **kwargs):
        self.filter_data = None
        super().__init__(**kwargs)

    def filter_queryset(self, queryset):
        """
        过滤查询集
        """
        if self.filter_data:
            filter_data = self.filter_data
            if 'username' in filter_data:
                filter_data['user__username__contains'] = filter_data.pop('username')
            if 'handover_username' in filter_data:
                filter_data['handover_user__username__contains'] = filter_data.pop('handover_username')
            if 'department_id' in filter_data:
                filter_data['user__department'] = filter_data.pop('department_id')
            if 'start_time' in filter_data:
                filter_data['job_time__gte'] = filter_data.pop('start_time')
            if 'end_time' in filter_data:
                filter_data['job_time__lte'] = filter_data.pop('end_time')
            query_set = queryset.filter(**filter_data).order_by('-job_time')
        else:
            query_set = super().filter_queryset(queryset).order_by('-job_time')

        return query_set

    def get(self, request, *args, **kwargs):
        """员工日志列表"""
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)

        self.filter_data = serializer.validated_data
        return super().get(request, *args, **kwargs)

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
        validated_data = [self.validate_create(validated_data) for validated_data in
                          serializer.validated_data]
        return validated_data

    def validate_create(self, validated_data):
        """验证参数"""
        handover_user = validated_data.get('handover_user')
        handover_content = validated_data.get('handover_content')
        job_content = validated_data.get('job_content')
        is_handover = validated_data.get('is_handover')
        validated_data['user'] = self.request.user
        if is_handover is None:
            self.param_error(code=ErrorType.NULL, param_name='is_handover')
        if is_handover is True:
            if not handover_user:
                self.param_error(code=ErrorType.BLANK, param_name='handover_user')
            if not handover_content:
                self.param_error(code=ErrorType.BLANK, param_name='handover_content')
            if not self.request.user.is_superuser:
                if handover_user.department != self.request.user.department:
                    self.param_error(code=ErrorType.INVALID_CHOICE, param_name='handover_user')
            return validated_data
        validated_data['handover_user'] = self.request.user
        if not handover_content:
            validated_data['handover_content'] = job_content
        return validated_data


class UserDiaryDownloadView(ListCustomAPIView):
    """用户日志下载
       user_diary_download:用户日志下载
   """
    serializer_class = serializers.UserDiarySerializer
    queryset = UserDiary.objects.all().only('id')

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
            if 'username' in filter_data:
                filter_data['user__username__contains'] = filter_data.pop('username')
            if 'handover_username' in filter_data:
                filter_data['handover_user__username__contains'] = filter_data.pop('handover_username')
            if 'department_id' in filter_data:
                filter_data['user__department'] = filter_data.pop('department_id')
            if 'start_time' in filter_data:
                filter_data['job_time__gte'] = filter_data.pop('start_time')
            if 'end_time' in filter_data:
                filter_data['job_time__lte'] = filter_data.pop('end_time')
            query_set = queryset.filter(**filter_data).order_by('-job_time')
        else:
            query_set = super().filter_queryset(queryset).order_by('-job_time')

        return query_set

    def get(self, request, *args, **kwargs):
        """工作日志列表"""
        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)

        self.filter_data = serializer.validated_data
        response = super().get(request, *args, **kwargs)
        data = response.data
        if data.get('objects'):
            self._data = response.data['objects']
            return self.user_diary_download()
        return self.download_empty_excel()

    def user_diary_download(self):
        """下载员工日志"""
        work_book = self.structure_excel_data()
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('diary.xls')
        response.write(sio.getvalue())

        return response

    def structure_excel_data(self):
        """构造excel数据"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'工作日志')
        work_book_data.write(0, 0, u'员工姓名')
        work_book_data.write(0, 1, u'工作内容')
        work_book_data.write(0, 2, u'时间')
        work_book_data.write(0, 3, u'是否交接')
        work_book_data.write(0, 4, u'交接人')
        work_book_data.write(0, 5, u'交接内容')
        work_book_data.write(0, 6, u'是否确认交接')
        # 写入数据
        excel_row = 1
        for diary_info in self._data:
            username = diary_info['username']
            job_content = diary_info['job_content']
            job_time = diary_info['job_time']
            is_handover = is_confirm = '是'
            if diary_info['is_handover'] is False:
                is_handover = '否'
            if diary_info['is_confirm'] is False:
                is_confirm = '否'
            handover_username = diary_info['handover_username']
            handover_content = diary_info['handover_content']

            work_book_data.write(excel_row, 0, username)
            work_book_data.write(excel_row, 1, job_content)
            work_book_data.write(excel_row, 2, job_time)
            work_book_data.write(excel_row, 3, is_handover)
            work_book_data.write(excel_row, 4, handover_username)
            work_book_data.write(excel_row, 5, handover_content)
            work_book_data.write(excel_row, 6, is_confirm)

            excel_row += 1

        # work_book.save("diary.xls")

        return work_book

    @staticmethod
    def download_empty_excel():
        """下载用户日志模板"""
        work_book = Workbook(encoding="UTF-8")
        work_book_data = work_book.add_sheet(u'工作日志')
        work_book_data.write(0, 0, u'员工姓名')
        work_book_data.write(0, 1, u'工作内容')
        work_book_data.write(0, 2, u'时间')
        work_book_data.write(0, 3, u'是否交接')
        work_book_data.write(0, 4, u'交接人')
        work_book_data.write(0, 5, u'交接内容')
        work_book_data.write(0, 6, u'是否确认交接')
        # work_book.save("diary.xls")
        sio = BytesIO()
        work_book.save(sio)
        sio.seek(0)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('diary.xls')
        response.write(sio.getvalue())

        return response


class UserDiaryDetail(RetrieveUpdateCustomAPIView):
    """获取用户日志详情
        get:获取用户日志详情
    """
    serializer_class = serializers.UserDiarySerializer
    queryset = UserDiary.objects.all().only('id')

    def get_serializer_class(self):
        """根据请求方式返回对应的序列化器类"""
        if self.request.method == 'PUT':
            return serializers.UserDiaryConfirmSerializer
        return self.serializer_class


class PlanInfoView(CreateListCustomAPIView):
    """预案信息管理
    GET:预案列表
    POST:新增预案
    """
    serializer_class = serializers.PlanInfoSerializer
    queryset = PlanInfo.objects.only('id').all().order_by('-id')

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

            if 'plan_name' in filter_data:
                filter_data['plan_name__contains'] = filter_data.pop('plan_name')
            if 'plan_code' in filter_data:
                filter_data['plan_code__contains'] = filter_data.pop('plan_code')
            if 'keywords' in filter_data:
                filter_data['keywords__contains'] = filter_data.pop('keywords')

            queryset = queryset.filter(**filter_data)

        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        """根据请求方式返回对应的序列化器类"""
        if self.request.method == 'GET':
            return serializers.PlanInfoListSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        """
        预案列表
        """

        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.filter_data = serializer.validated_data
        return super().list(request, *args, **kwargs)


class PlanInfoDownLoadDeleteView(mixins.RetrieveModelMixin, CustomGenericAPIView):
    """预案信息管理
        GET:预案文件下载
        """
    serializer_class = serializers.PlanInfoSerializer
    queryset = PlanInfo.objects.only('id').all().order_by('-id')

    def get(self, request, *args, **kwargs):
        """预案文件下载"""
        # 获取预案对象
        instance = self.get_object()

        # 获取预案文件、预案文件路径、预案文件名
        doc_file = instance.doc_file
        doc_path = doc_file.path
        doc_name = doc_file.name[10:]

        # 读取预案文件
        file = self.file_iterator(doc_path)

        # 构造响应
        response = FileResponse(file)
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(escape_uri_path(doc_name))

        return response

    def file_iterator(self, doc_path):
        """打开文件"""
        if os.path.exists(doc_path):
            # 如果文件存在则下载
            file = open(doc_path, 'rb')
            return file
        self.param_error(errcode=RET.EXPARAMERR, errmsg='预案文件不存在')


class PlanInfoUpdateDeleteView(RetrieveUpdateCustomAPIView, mixins.DestroyModelMixin):
    """预案信息管理
        GET:预案详情
        PUT:预案修改
        DELETE:预案删除，同时删除预案文件
        """
    serializer_class = serializers.PlanInfoUpdateSerializer
    queryset = PlanInfo.objects.only('id').all().order_by('-id')

    def delete(self, request, *args, **kwargs):
        """删除预案，同时删除预案文件"""
        instance = self.get_object()
        self.remove_file(instance)
        self.perform_destroy(instance)

        return self.success_response(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def remove_file(instance):
        """删除预案文件"""
        doc_file = instance.doc_file
        doc_path = doc_file.path

        # 如果文件存在则删除
        if os.path.exists(doc_path):
            os.remove(doc_path)


class MqMessageStatisticsView(CustomGenericAPIView):
    metrics_key_name = 'system_metrics_{date}'
    system_list = ['zvams', 'vms', 'acs', 'cms', 'ais', 'xfhz', 'ybbj', 'ps', 'iis', 'iis_publish']

    def get(self, request):
        data = {system: 0 for system in self.system_list}
        cache_redis_conn = get_redis_connection('cache')

        system_metrics = cache_redis_conn.hgetall(self.metrics_key_name.format(date=datetime.now().date()))
        for system, msg_count in system_metrics.items():
            data[system.decode()] = int(msg_count.decode())

        return self.success_response(data=data)


class StaffInfoView(CreateListCustomAPIView):
    """员工信息管理
    GET:员工列表
    POST:创建员工
    """
    serializer_class = serializers.StaffInfoSerializer
    queryset = StaffInfo.objects.only('id').all().order_by(Convert('staff_name', 'gbk').asc())

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

            if 'staff_name' in filter_data:
                filter_data['staff_name__contains'] = filter_data.pop('staff_name')
            if 'phone_number' in filter_data:
                filter_data['phone_number__contains'] = filter_data.pop('phone_number')
            if 'department' in filter_data and filter_data['department'] is None:
                del filter_data['department']

            queryset = queryset.filter(**filter_data)

        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        """根据请求方式返回对应的序列化器类"""
        if self.request.method == 'GET':
            return serializers.StaffInfoListSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        """
        员工列表
        """

        serializer = self.get_serializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        self.filter_data = serializer.validated_data
        return super().list(request, *args, **kwargs)


class StaffInfoDetailView(RetrieveUpdateCustomAPIView, mixins.DestroyModelMixin):
    """员工信息详情管理
        get:获取用户日志详情
    """
    serializer_class = serializers.StaffInfoSerializer
    queryset = StaffInfo.objects.only('id').all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
