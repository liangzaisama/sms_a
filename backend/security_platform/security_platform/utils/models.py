"""
抽象模块类文件
"""
from abc import ABC

from django.db import models

from django.db.models import Manager, Func


class FilterIsDeletedManager(Manager):
    """
    逻辑删除的影响：

    本模型查询一律无法查到：包括filter、get、all

    一对多关系：
    如果被删除的是1：那么多的那方不受影响、还能正常查询及关系的信息  举例：用户>用户日志
    result = UserDiary.objects.all()[0]
    print(result.user.username)

    如果被删除的是多：根据1查多的时候无法查询到被删除的多 举例：用户>部门
    department = Department.objects.get(id=4)
    print(department.user_set.filter(username=100191216))

    多对多关系:
    某一方多被删除、进行关联查询的时候均无法查到 举例：设备>用户
    device = DeviceInfo.objects.all().first()
    print(device)
    print(device.users.all())

    总结：直接查询和关联查询均无法找到对应的模型对象
    """

    def get_queryset(self):
        """过滤逻辑删除的记录"""
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    """为模型类补充字段"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class Convert(Func, ABC):
    """转换中文字段编码格式，解决排序问题"""
    def __init__(self, expression, transcoding_name, **extra):
        super(Convert, self).__init__(
            expression=expression, transcoding_name=transcoding_name, **extra)

    def as_mysql(self, compiler, connection):
        self.function = 'CONVERT'
        self.template = ' %(function)s(%(expression)s USING  %(transcoding_name)s)'
        return super(Convert, self).as_sql(compiler, connection)
