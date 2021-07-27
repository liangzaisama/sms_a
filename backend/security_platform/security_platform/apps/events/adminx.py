import xadmin

from . import models


class AlarmEventAdmin:
    list_display = ['id', 'create_time', 'event_name', 'event_type', 'event_code', 'area_code', 'priority', 'event_state']
    ordering = ['-id']
    list_filter = ['priority', 'event_name', 'event_type']
    list_editable = ['event_type', 'event_state', 'create_time']


class PeopleCountingRecordAdmin:
    list_display = ['camera', 'statistical_time', 'total_people']
    ordering = ['id', 'statistical_time']


xadmin.site.register(models.AlarmEvent, AlarmEventAdmin)
xadmin.site.register(models.DeviceAlarmEvent, AlarmEventAdmin)
xadmin.site.register(models.PersonAlarmEvent, AlarmEventAdmin)
xadmin.site.register(models.DeviceAlarmEventPicture)
xadmin.site.register(models.DeviceAlarmEventCamera)
xadmin.site.register(models.EventWorkSheet)

xadmin.site.register(models.DeployAlarmRecord)
xadmin.site.register(models.DeployPersonSnapRecord)
xadmin.site.register(models.PersonDensityRecord)
xadmin.site.register(models.BehaviorAlarmRecord)
xadmin.site.register(models.PlaceAlarmRecord)
xadmin.site.register(models.PlaceSafeguardRecord)
xadmin.site.register(models.PostureAlarmRecord)
xadmin.site.register(models.PeopleCountingRecord, PeopleCountingRecordAdmin)
xadmin.site.register(models.CameraLineUpRecord)
