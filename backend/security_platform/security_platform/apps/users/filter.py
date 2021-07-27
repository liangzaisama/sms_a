"""用户接口数据过滤器

UserFilterBackend：用户列表接口过滤器
DevicePermFilter：用户设备权限设备过滤器
UserPermFilter：用户操作用户相关接口时权限过滤器
"""

from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend

from users.models import User, Department
from devices.models import DeviceInfo


class UserFilterBackend(BaseFilterBackend):
    """用户列表字段过滤"""

    filter_data = None

    def add_filter_field_by_level(self, level):
        """根据用户等级添加过滤字段

        Args:
            level: 用户等级
        """
        self.filter_data.update(User.get_field_value_by_level(level))

    def filter_queryset(self, request, queryset, view):
        """对原始查询集进行过滤

        Args:
            request: 请求对象
            queryset: 原始查询集
            view: 视图对象

        Returns:
            result: 过滤后的查询集
        """
        self.filter_data = view.validate_data

        if 'level' in self.filter_data:
            # 存在等级
            level_filter_data = User.get_field_value_by_level(self.filter_data.pop('level'))
            self.filter_data.update(level_filter_data)

        if 'staff_name' in self.filter_data:
            self.filter_data['staff_name__icontains'] = self.filter_data.pop('staff_name')

        result = queryset.filter(**self.filter_data)
        # print(result.query)
        # print(result.explain())
        return result


class UserFilter(filters.FilterSet):
    """摄像机过滤器"""

    staff_name = filters.CharFilter(field_name="staff_name", lookup_expr='icontains')
    username = filters.CharFilter(field_name="username", lookup_expr='icontains')
    department_id = filters.ModelChoiceFilter(queryset=Department.objects.all().only('id'))
    level = filters.ChoiceFilter(choices=User.UserLevel.choices, method='filter_level')

    class Meta:
        model = User
        fields = ['username', 'staff_name', 'department_id', 'level']

    def filter_level(self, queryset, _, value):
        """过滤等级"""
        return queryset.filter(**User.get_field_value_by_level(value))


class DevicePermFilter(filters.FilterSet):
    """自定义设备权限过滤字段

    可通过device_name，device_code，device_type对设备进行过滤

    field_name: 对应模型类的字段
    lookup_expr: 过滤时对应的表达式
    """

    device_name = filters.CharFilter(field_name="device_name", lookup_expr='icontains')
    device_code = filters.CharFilter(field_name="device_code", lookup_expr='icontains')

    class Meta:
        """模型类配置"""
        model = DeviceInfo
        fields = ['device_type']


class UserPermFilter(BaseFilterBackend):
    """用户操作权限过滤

    过滤掉用户没有权限的用户对象

    超级管理员权限：不能操作自己
    部门管理员权限：不能操作自己、不能操作自己部门外的用户、不能操作比自己等级高的用户
    """

    def filter_queryset(self, request, queryset, view):
        """过滤用户查询集"""
        queryset = queryset.exclude(id=request.user.id)

        if not request.user.is_superuser:
            queryset = queryset.exclude(is_superuser=True).filter(department_id=request.user.department_id)

        return queryset
