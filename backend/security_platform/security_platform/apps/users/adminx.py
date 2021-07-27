"""
xadmin界面样式配置及用户模型类配置
"""
import xadmin
from xadmin import views

from .models import Department, UserDiary, UserIPWhiteList, UserBacklog


class BaseSetting:
    """xadmin的基本配置"""
    enable_themes = True  # 开启主题切换功能
    use_bootswatch = True


class GlobalSettings:
    """xadmin的全局配置"""
    site_title = "安保管理平台"  # 设置站点标题
    site_footer = "安保管理平台"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(Department)
xadmin.site.register(UserDiary)
xadmin.site.register(UserIPWhiteList)
xadmin.site.register(UserBacklog)
