"""
设备资源路由注册
router 视图集路由
urlpatterns 注册路由列表
"""
from django.urls import re_path
from rest_framework import routers

from . import views


urlpatterns = [

    # 摄像机截图
    re_path(r'^devices/(?P<pk>\d+)/screenshots$', views.DevicesScreenshotView.as_view()),

    re_path(r'^devices/statistics$', views.DeviceCountView.as_view()),

    # 设备类型完好百分比统计，不区分权限
    re_path(r'^devices/type/statistics$', views.DeviceTypePercentageCountView.as_view()),

    # 设备列表
    re_path(r'^devices$', views.DeviceInfoView.as_view()),

    # gis设备列表
    re_path(r'^devices/gis$', views.DeviceGisInfoView.as_view()),

    # 新增工单 POST、获取工单列表 GET
    re_path(r'^work/sheet$', views.WorkSheetView.as_view()),

    # 获取工单详情 GET
    re_path(r'^work/sheet/(?P<pk>\d+)$', views.WorkSheetRetrieveView.as_view()),

    # 工单审核 PUT
    re_path(r'^work/sheet/(?P<pk>\d+)/audit$', views.WorkSheetAuditView.as_view()),

    # 工单关闭 PUT
    re_path(r'^work/sheet/(?P<pk>\d+)/close$', views.WorkSheetCloseView.as_view()),
]

router = routers.DefaultRouter(trailing_slash=False)

# 设备维修记录
router.register(r'^devices/maintenance/records', views.DeviceMaintenanceRecordsViewSet,
                base_name='/records')

# 设备基本信息
router.register(r'^devices', views.DeviceBasicsViewSet, base_name='/devices')

# 设备组信息
router.register(r'^groups', views.DeviceGroupsViewSet, base_name='/groups')

# 标签信息
router.register(r'^labels', views.DeviceLabelsViewSet, base_name='/labels')

urlpatterns += router.urls
