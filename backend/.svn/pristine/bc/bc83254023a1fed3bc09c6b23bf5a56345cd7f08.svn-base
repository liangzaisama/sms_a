import math
import numpy as np


from rest_framework.filters import BaseFilterBackend


class DeviceObjectPermissionsFilter(BaseFilterBackend):
    """
    设备权限过滤
    """

    def filter_department_user_queryset(self, user, queryset):
        """
        过滤部门用户的设备权限

        Args:
            user:
            queryset:

        Returns:

        """
        if user.is_leader:
            # 部门领导
            return queryset.filter(departments=user.department_id)

        # 部门员工
        return queryset.filter(users=user, departments=user.department_id)

        # user_device_queryset = queryset.filter(users=user)
        # department_device_queryset = queryset.filter(departments=user.department_id)

        # if not user.is_leader:
        #     return user_device_queryset
        #
        # return user_device_queryset.union(department_device_queryset)

    def filter_queryset(self, request, queryset, view):
        """根据用户的级别返回不同查询集

        超级管理员：所有设备
        部门领导：部门设备权限
        部门员工：用户设备权限
        """
        user = request.user
        if not user.is_authenticated:
            # 未认证的用户
            return queryset.none()

        if user.is_superuser:
            # 超级用户不用过滤
            return queryset

        return self.filter_department_user_queryset(user, queryset)


class DeviceInfoListFilter(BaseFilterBackend):
    """
    根据设备字段进行过滤
    """

    def remove_invalid_fields(self, filter_data):
        """无效字段删除"""
        if 'scene' in filter_data:
            filter_data.pop('scene')

    def fuzzy_fields_transform(self, filter_data):
        """模糊查询字段转化"""
        if 'device_name' in filter_data:
            filter_data['device_name__icontains'] = filter_data.pop('device_name')

        if 'area_code' in filter_data:
            filter_data['area_code__icontains'] = filter_data.pop('area_code')

        if 'ipv4' in filter_data:
            filter_data['ipv4__icontains'] = filter_data.pop('ipv4')

    def related_filed_transform(self, filter_data):
        """关系查询字段转化"""
        if 'group_id' in filter_data:
            filter_data['group'] = filter_data.pop('group_id')

        if 'label_id' in filter_data:
            filter_data['label'] = filter_data.pop('label_id')

    def get_filter(self, request, queryset, view):
        filter_data = view.validate_data.copy()
        self.remove_invalid_fields(filter_data)
        self.fuzzy_fields_transform(filter_data)
        self.related_filed_transform(filter_data)

        return filter_data

    def filter_queryset(self, request, queryset, view):
        filter_data = self.get_filter(request, queryset, view)

        if filter_data:
            return queryset.filter(**filter_data)

        return queryset


class DeviceExcludeFilter(BaseFilterBackend):
    """通过用户或部门排除查询集"""

    def filter_queryset(self, request, queryset, view):
        """排除查询集"""
        if 'exclude_department_id' in view.validate_data:
            queryset = queryset.exclude(departments=view.validate_data.pop('exclude_department_id'))

        if 'exclude_user_id' in view.validate_data:
            queryset = queryset.exclude(users=view.validate_data.pop('exclude_user_id'))

        return queryset


class DeviceRelateObjectPermissionsFilter(BaseFilterBackend):
    """
    设备关联表权限过滤
    """

    def filter_department_user_queryset(self, user, queryset):
        """
        过滤部门用户的设备权限

        Args:
            user:
            queryset:

        Returns:

        """
        if user.is_leader:
            # 部门领导
            return queryset.filter(device_info__departments=user.department_id)

        # 部门员工
        return queryset.filter(device_info__users=user, device_info__departments=user.department_id)

        # user_device_queryset = queryset.filter(users=user)
        # department_device_queryset = queryset.filter(departments=user.department_id)
        #
        # if not user.is_leader:
        #     return user_device_queryset
        #
        # return user_device_queryset.union(department_device_queryset)

    def filter_queryset(self, request, queryset, view):
        """根据用户的级别返回不同查询集

        超级管理员：所有设备
        部门领导：部门设备权限
        部门员工：用户设备权限
        """
        user = request.user

        if user.is_superuser:
            # 超级用户不用过滤
            return queryset

        return self.filter_department_user_queryset(user, queryset)


class DeviceGisRadiusFilter(BaseFilterBackend):
    """
    设备gis半径过滤
    """

    def calculate_cover_radius_devices(self, filter_data, queryset):
        """计算获取gis点位半径内的摄像机设备，返回新的设备列表"""

        gis_field = filter_data.get('gis_basic_info')
        cover_radius = float(filter_data.get('cover_radius'))
        new_queryset = []

        for device_info in queryset:
            # 将设备gis信息转化为浮点数
            if device_info.gis_basic_info:
                # 过滤掉没有gis信息的摄像机设备
                device_gis = [float(gis_info) for gis_info in device_info.gis_basic_info.split(',')]
                np_gis = np.array(gis_field)
                np_device = np.array(device_gis)
                np_different = np_device - np_gis
                length = math.hypot(np_different[0], np_different[1])
                # 两点间距离小于输入半径，则加入设备列表
                if length < cover_radius:
                    new_queryset.append(device_info)

        return new_queryset

    def filter_queryset(self, request, queryset, view):
        filter_data = view.validate_data.copy()
        queryset = self.calculate_cover_radius_devices(filter_data, queryset)

        return queryset
