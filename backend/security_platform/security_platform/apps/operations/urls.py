"""
安保运行管理模块路由注册
urlpatterns 注册路由列表
"""
from django.urls import re_path

from . import views

urlpatterns = [

    # 获取值班通讯录列表
    re_path(r'^contact$', views.WatchAddressBookView.as_view()),

    # 上传值班通讯录
    re_path(r'^contact/imports$', views.WatchAddressUploadBookView.as_view()),

    # 下载值班通讯录
    re_path(r'^contact/exports$', views.WatchAddressBookDownloadView.as_view()),

    # 下载值班通讯录模板
    re_path(r'^contact/exports/template$', views.WatchAddressBookTemplateDownloadView.as_view()),

    # 获取门禁通行记录列表
    re_path(r'^access/records$', views.AccessRecordsView.as_view()),

    # 获取用户日志列表、新增用户日志
    re_path(r'^users/diary$', views.UserDiaryView.as_view()),

    # 下载日志列表
    re_path(r'^users/diary/exports$', views.UserDiaryDownloadView.as_view()),

    # 用户日志详情
    re_path(r'^users/diary/(?P<pk>\d+)', views.UserDiaryDetail.as_view()),

    # 获取预案列表、新增预案
    re_path(r'^plan$', views.PlanInfoView.as_view()),

    # 预案文件修改、预案删除
    re_path(r'^plan/(?P<pk>\d+)$', views.PlanInfoUpdateDeleteView.as_view()),

    # 预案文件下载
    re_path(r'^plan/(?P<pk>\d+)/export$', views.PlanInfoDownLoadDeleteView.as_view()),

    # mq统计信息
    re_path(r'^mq', views.MqMessageStatisticsView.as_view()),

    # 获取员工列表、新增员工
    re_path(r'^staff$', views.StaffInfoView.as_view()),

    # 获取员工详情、员工信息修改、删除
    re_path(r'^staff/(?P<pk>\d+)$', views.StaffInfoDetailView.as_view()),

]
