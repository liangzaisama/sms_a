from django.urls import re_path

from . import views

urlpatterns = [

    # 获取运行天数
    re_path(r'^runday$', views.RunDayView.as_view()),

    # 获取摄像机列表
    re_path(r'^cameras$', views.CameraView.as_view()),

    # 航班信息
    re_path(r'^flight/resource$', views.FlightResourceView.as_view()),

    # 道口车辆通行记录
    re_path(r'^vehicle$', views.CarPassThroughView.as_view()),

    # 出入口
    re_path(r'^passageways$', views.PassagewayView.as_view()),

    # 值机柜台信息
    re_path(r'^counters$', views.CheckInCounterView.as_view()),

    # 安检口信息
    re_path(r'^securities$', views.SecurityCheckView.as_view()),

    # 登机口信息
    re_path(r'^gates$', views.BoardingGateView.as_view()),

    # 反向通道信息
    re_path(r'^channels$', views.ReverseChannelView.as_view()),

    # 机位信息
    re_path(r'^placements$', views.PlacementView.as_view()),

    # 行李转盘信息
    # re_path(r'^turntables$', views.BaggageTurntableView.as_view()),

]
