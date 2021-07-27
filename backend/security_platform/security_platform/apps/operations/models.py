"""安保运行管理模型类"""
import time
from collections import OrderedDict

from django.db import models

from users.models import Department
from security_platform import IntegerChoices, TextChoices
from security_platform.utils.models import BaseModel


class WatchAddressBook(BaseModel):
    """值班通讯录"""

    department_name = models.CharField('部门名称', max_length=20)
    staff_name = models.CharField('值班人员', max_length=10)
    contact_mobile = models.CharField('联系电话', max_length=20)
    duty_date = models.DateField('值班日期')

    class Meta:
        verbose_name = '值班通讯录'
        verbose_name_plural = verbose_name
        db_table = 'tb_watch_address_book'


class EntranceAccessRecords(BaseModel):
    """门禁通行记录"""

    class InOutChoice(IntegerChoices):
        IN = 0, '进'
        OUT = 1, '出'

    entrance_punch_code = models.CharField(max_length=40, verbose_name='门禁刷卡编码')
    device_code = models.CharField(max_length=200, verbose_name='门禁设备编码')
    device_name = models.CharField(verbose_name='门禁设备名称', max_length=60)
    record_time = models.DateTimeField(verbose_name='门禁刷卡时间')
    card_no = models.CharField(max_length=30, verbose_name='卡号')
    holder = models.CharField(max_length=32, verbose_name='持卡人姓名')
    department = models.CharField(max_length=64, verbose_name='部门名称', blank=True)
    jobs = models.CharField(max_length=64, verbose_name='岗位', blank=True)
    code_name = models.CharField(max_length=64, verbose_name='门禁代号', blank=True)
    in_out = models.SmallIntegerField(choices=InOutChoice.choices, verbose_name='进出方向')
    region_id = models.CharField(max_length=10, verbose_name='刷卡区域id')

    WS_URL_SUFFIX = 'entrance_access'

    class Meta:
        verbose_name = '门禁通行记录'
        verbose_name_plural = verbose_name
        db_table = 'tb_entrance_access_records'

    @property
    def ws_message(self):
        """实时排队websocket消息构造"""
        message = OrderedDict()
        message['entrance_punch_code'] = self.entrance_punch_code
        message['device_code'] = self.device_code
        # message['device_name'] = self.device_name
        message['record_time'] = str(self.record_time)
        message['card_no'] = self.card_no
        message['holder'] = self.holder
        message['department'] = self.department
        message['jobs'] = self.jobs
        message['code_name'] = self.code_name
        message['in_out'] = self.in_out
        message['region_id'] = self.region_id

        return message


# 三检要求
class PlanInfo(BaseModel):
    """预案信息"""
    plan_name = models.CharField('预案名称', max_length=20, blank=False)
    plan_code = models.CharField('预案编码', max_length=20, blank=False)
    keywords = models.CharField('关键字', max_length=10, blank=False)
    description = models.TextField('预案说明', blank=True)
    gis_basic_info = models.TextField('gis基础信息', blank=False)
    gis_field = models.TextField('gis点位信息', blank=False)
    doc_file = models.FileField('文件地址', upload_to='plan_file', blank=False)

    @classmethod
    def generate_plan_code(cls):
        """生成预案ID

        根据P+时间戳保留4位小数拼接字段串

        Returns:
            event_code: 预案ID
        """
        return 'P{0}'.format(str(round(time.time(), 4)).replace('.', ''))

    class Meta:
        verbose_name = '预案信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_plan_info'

    def __str__(self):
        return self.plan_name


# 三检要求
class StaffInfo(BaseModel):
    """员工信息"""

    class SexType(TextChoices):
        MALE = 'male', '男'
        FEMALE = 'female', '女'
        OTHER = 'other', '其它'

    class StaffType(TextChoices):
        AB = 'ab', '安保'
        AJ = 'aj', '安检'
        XF = 'xf', '消防'
        OTHER = 'other', '其它'

    class CardType(TextChoices):
        """证件类型"""
        LONG = 'L', '长期'
        SHORT = 'S', '短期'
        TEMPORARY = 'T', '临时'
        GUARD = 'G', '警卫'
        EMERGENCY = 'E', '应急'

    class CardStatus(IntegerChoices):
        """证件状态"""
        NORMAL = 1, '正常'
        APPLY = 2, '申请'
        CHANGE = 3, '变更'
        LOSS = 4, '挂失'
        REPLACE = 5, '补办'
        LOSSD = 6, '已挂失'
        RECYCLE = 7, '已回收'
        EMERGENCY = 8, '待申请'
        EXPIRE = 9, '到期'
        CANCEL = 10, '注销'

    # 卡证字段
    staff_name = models.CharField('员工姓名', max_length=10)
    sex = models.CharField('性别', max_length=10, choices=SexType.choices, default='male')
    birthday = models.DateField('出生日期')
    phone_number = models.CharField('联系电话', max_length=20)
    entry_date = models.DateField('入职日期')
    picture = models.TextField('照片', blank=True)
    gis_basic_info = models.TextField('gis基础信息', blank=True)
    gis_field = models.CharField('gis点位信息(x,y)', blank=True, max_length=100)
    description = models.TextField('备注', blank=True)
    pass_card_number = models.CharField('通行证卡号', max_length=35, blank=True)
    work_number = models.CharField('工号', max_length=55, unique=True, null=True, blank=True)
    identity_card = models.CharField('身份证', max_length=30, blank=True)
    address = models.CharField('住址', max_length=100, blank=True)
    country = models.CharField('国籍', max_length=20, blank=True)
    nation = models.CharField('民族', max_length=10, blank=True)
    jobs = models.CharField('岗位', max_length=20, blank=True)
    department_name = models.CharField('部门名称', max_length=20, blank=True)
    son_department_name = models.CharField('子部门名称', max_length=20, blank=True)
    pass_area = models.TextField('通行区域', blank=True)
    entrances_area = models.TextField('门禁区域', blank=True)
    pass_card_type = models.CharField('卡证类型', max_length=1, blank=True, choices=CardType.choices)
    card_create_time = models.DateField('制证日期', null=True, blank=True)
    card_handle_time = models.DateField('办证日期', null=True, blank=True)
    card_expire_time = models.DateField('超期日期', null=True, blank=True)
    is_black = models.BooleanField('是否黑名单', null=True, blank=True)
    is_lock = models.BooleanField('是否锁定', null=True, blank=True)
    black_reason = models.CharField('黑名单原因', max_length=100, blank=True)
    lock_reason = models.CharField('锁定原因', max_length=100, blank=True)
    card_status = models.SmallIntegerField('卡证状态', choices=CardStatus.choices, null=True, blank=True)
    score = models.IntegerField('当前积分', null=True, blank=True)
    pass_card_max_count = models.IntegerField('最大允许通行次数', null=True, blank=True)
    pass_card_current_count = models.IntegerField('已通行次数', null=True, blank=True)

    # 未知
    department = models.ForeignKey(Department, verbose_name='所属部门', on_delete=models.PROTECT, null=True, blank=True)
    staff_type = models.CharField('类型', max_length=10, choices=StaffType.choices, default='ab')

    class Meta:
        verbose_name = '员工信息'
        verbose_name_plural = verbose_name
        db_table = 'tb_staff_info'

    def __str__(self):
        return self.staff_name

# 三检要求
# class TrainInfo(models.Model):
#     """员工培训信息"""
#     staff = models.ForeignKey(StaffInfo, verbose_name="员工", on_delete=models.CASCADE)
#     train_course = models.CharField('培训课程', max_length=50)
#     train_result = models.CharField('培训结果', max_length=50)
#     start_time = models.DateField('开始时间')
#     end_time = models.DateField('结束时间')
#
#     class Meta:
#         verbose_name = '培训信息'
#         verbose_name_plural = verbose_name
#         db_table = 'tb_train_info'


# 三检要求
# class QualificationInfo(models.Model):
#     """员工资质信息"""
#     staff = models.ForeignKey(StaffInfo, verbose_name="员工", on_delete=models.CASCADE)
#     qualification_record = models.CharField('资质记录', max_length=50)
#     award_date = models.DateField('颁发时间')
#     award_unit = models.CharField('颁发单位', max_length=50)
#
#     class Meta:
#         verbose_name = '资质信息'
#         verbose_name_plural = verbose_name
#         db_table = 'tb_qualification_info'
