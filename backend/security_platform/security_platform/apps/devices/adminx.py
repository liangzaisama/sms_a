import xadmin

from . import models


class DeviceInfoAdmin:
    list_display = ['id', 'create_time', 'device_name', 'device_code', 'device_type',
                    'device_state', 'resource', 'area_code', 'trouble_code', 'trouble_message']
    refresh_times = [3, 5]
    ordering = ['-id']
    list_editable = ['device_type', 'device_state', 'resource__resource_type', 'resource']
    list_filter = ['device_type', 'device_name', 'resource__resource_type', 'device_code', 'device_type']


# class CameraAdmin(DeviceInfoAdmin):
#     list_display = DeviceInfoAdmin.list_display + ['resource']
#     list_editable = DeviceInfoAdmin.list_editable + ['resource']
#     list_filter = ['device_type', 'device_name', 'device_code', 'resource__resource_type', 'resource__name']


class CameraDeviceAdmin:
    list_display = ['create_time', 'camera_type', 'point_angel', 'visual_angel', 'cover_radius', 'install_height']
    list_filter = ['camera_type']
    refresh_times = [3, 5]
    ordering = ['-create_time']


class EntranceSlotCardRecordAdmin:
    list_display = ['entrance_punch_code', 'device_code', 'record_time', 'card_no', 'holder', 'in_out']
    # style_fields = {'device_code': 'm2m_transfer'}


class GroupsAdmin:
    list_display = ['id', 'name', 'user']
    refresh_times = [3, 5]
    ordering = ['id']


# class PersonDensityRecordAdmin:
#     list_display = ['camera', 'total_people_number', 'alarm_time', 'alarm_image_url', 'alarm_level']
#     ordering = ['id', 'alarm_time']


xadmin.site.register(models.DeviceInfo, DeviceInfoAdmin)
xadmin.site.register(models.CameraDevice, DeviceInfoAdmin)
xadmin.site.register(models.MaintenanceDevice, DeviceInfoAdmin)
xadmin.site.register(models.FireDevice, DeviceInfoAdmin)
xadmin.site.register(models.ConcealAlarmDevice, DeviceInfoAdmin)
xadmin.site.register(models.EntranceDevice, DeviceInfoAdmin)
xadmin.site.register(models.PassageWayDevice, DeviceInfoAdmin)
xadmin.site.register(models.DeviceGroup, GroupsAdmin)
xadmin.site.register(models.DeviceLabel, GroupsAdmin)
xadmin.site.register(models.WorkSheet)
xadmin.site.register(models.DeviceMaintenanceRecords)
