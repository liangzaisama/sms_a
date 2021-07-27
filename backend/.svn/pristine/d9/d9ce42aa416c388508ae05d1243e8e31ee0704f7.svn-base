"""
报警事件路由注册
router 视图集路由
urlpatterns 注册路由列表
"""
from django.urls import re_path
from rest_framework import routers

from events import views


urlpatterns = [

    # 排队统计
    re_path(r'^queues$', views.QueueStatisticsView.as_view()),

    # 布控报警记录
    re_path(r'^depoly/alarm$', views.DeployAlarmView.as_view()),

    # 布控抓拍记录
    re_path(r'^depoly/snap$', views.DeploySnapView.as_view()),

    # 客流分析
    re_path(r'^passengers$', views.PassengerFlowView.as_view()),

    # 机位保障
    re_path(r'^placements/safeguard$', views.PlacementSafeguardView.as_view()),

    # 机位报警
    re_path(r'^placements/alarm$', views.PlacementAlarmView.as_view()),

    # 密度报警记录
    re_path(r'^densities$', views.DensityAlarmView.as_view()),

    # 姿态报警记录
    re_path(r'^postures$', views.PostureAlarmView.as_view()),

    # 围界报警记录 围界版
    # re_path(r'^scopes$', views.ScopesAlarmView.as_view()),

    # 围界报警记录 监控webapi版
    re_path(r'^scopes$', views.MonitorScopesAlarmView.as_view()),

    # 事件工单列表
    re_path(r'^events/work/sheet$', views.AlarmEventWorkSheetView.as_view()),

    # 当前用户已指派的待处置事件ID列表
    re_path(r'^events/work/sheet/user$', views.UserAlarmEventWorkSheetView.as_view()),

    # 事件工单误派销单
    re_path(r'^events/work/sheet/(?P<pk>\d+)$', views.AlarmEventWorkSheetCloseView.as_view()),

]

router = routers.DefaultRouter(trailing_slash=False)

# 报警事件
router.register(r'^alarm/events', views.AlarmEventViewSet, base_name='/events')

urlpatterns += router.urls
