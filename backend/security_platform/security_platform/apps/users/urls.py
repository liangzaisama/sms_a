"""用户模块api路由地址

包含三部分接口
1. 用户登录及登录后相关操作接口，登录/修改场景值/修改密码/
2. 高级别用户操作低级别用户相关接口，重置用户密码/修改用户信息/新增用户/批量注销
3. 用户权限相关接口，部门页面权限/设备权限/员工设备权限
"""
from django.urls import re_path

from . import views


urlpatterns = [

    # 获取部门列表
    re_path(r'^departments$', views.DepartmentView.as_view()),

    # 部门页面权限获取、修改
    re_path(r'^departments/(?P<pk>\d+)/page-permissions$', views.DepartmentPagePermissionView.as_view()),

    # 部门设备权限修改、获取
    re_path(r'^departments/(?P<pk>\d+)/device-permissions$', views.DepartmentDevicePermissionView.as_view()),

    # 登录
    re_path(r'^authorizations$', views.UserAuthorizeView.as_view()),

    # 修改用户场景值（用户登录） PUT
    re_path(r'^users/scenario$', views.UserScenarioView.as_view()),

    # 修改用户密码（用户登录）  PUT
    re_path(r'^users/password$', views.UserPasswordView.as_view()),

    # 用户待办事项 （用户登录）
    re_path(r'^users/backlog$', views.UserBacklogView.as_view()),

    # 重置用户密码（部门管理员及以上登录）  PUT
    re_path(r'^users/(?P<pk>\d+)/password/default$', views.UserPasswordDefaultView.as_view()),

    # 修改用户信息 (部门管理员及以上登录) PUT
    re_path(r'^users/(?P<pk>\d+)$', views.UserInfoUpdateView.as_view()),

    # 新增用户(部门管理员及以上登录) POST、获取用户列表 GET 无权限控制
    re_path(r'^users$', views.UserInfoView.as_view()),

    # 用户权限克隆
    re_path(r'^users/(?P<pk>\d+)/clones$', views.UserCloneView.as_view()),

    # 批量注销
    re_path(r'^users/batch$', views.BatchUserView.as_view()),

    # 员工设备权限修改、获取
    re_path(r'^users/(?P<pk>\d+)/device-permissions$', views.UserDevicePermissionView.as_view()),

    # 用户ip查询, 用户ip增加，根据用户id查询
    re_path(r'^users/(?P<pk>\d+)/ip$', views.UserIpCreateListView.as_view()),

    # 用户ip修改，根据ip id查询
    re_path(r'^users/ip/(?P<pk>\d+)$', views.UserIpUpdateView.as_view()),

    # ip批量注销
    re_path(r'^users/ip/batch$', views.BatchUserIpView.as_view()),

]
