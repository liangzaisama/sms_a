from django.urls import re_path

from . import views

urlpatterns = [

    # 更新版本号查询
    re_path(r'^version$', views.GetVersionView.as_view()),
    # 系统参数配置
    re_path(r'^config$', views.ConfigListUpdateView.as_view()),
    # gis图片获取
    re_path(r'^gis$', views.GisListView.as_view()),

]
