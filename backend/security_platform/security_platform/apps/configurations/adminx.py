import xadmin

from . import models


class SystemConfigAdmin:
    list_display = ['config_key', 'config_value', 'is_exposed']
    list_editable = ['config_value']


class GisMapAdmin:
    list_display = ['map_id', 'map_class', 'map_name', 'map_type']


class GisLayerAdmin:
    list_display = ['layer_id', 'layer_name', 'layer_type', 'resource_name', 'remark', 'map']


xadmin.site.register(models.SystemConfig, SystemConfigAdmin)
xadmin.site.register(models.GisMap, GisMapAdmin)
xadmin.site.register(models.GisLayer, GisLayerAdmin)
xadmin.site.register(models.GisPoint)
