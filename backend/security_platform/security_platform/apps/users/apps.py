"""
用户模块app配置及用户初始化数据导入
"""
from django.conf import settings
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_super_user(**kwargs):
    """创建默认管理员用户"""
    from django.contrib.auth.hashers import make_password

    try:
        User = kwargs['apps'].get_model('users', 'User')
    except LookupError:
        return

    User.raw_objects.get_or_create(
        username=settings.API_SETTINGS.DEFAULT_SUPER_USER_NAME,
        defaults={
            'password': make_password(settings.API_SETTINGS.DEFAULT_USER_PASSWORD),
            'is_staff': True, 'is_superuser': True
        }
    )


def create_default_department(**kwargs):
    """创建默认部门数据"""
    try:
        Department = kwargs['apps'].get_model('users', 'Department')
    except LookupError:
        return

    if not Department.objects.count():
        for department_name in settings.API_SETTINGS.DEFAULT_DEPATMENT:
            Department.objects.get_or_create(department_name=department_name)


def create_default_department_user(**kwargs):
    """创建默认管理员用户"""
    from django.contrib.auth.hashers import make_password

    try:
        User = kwargs['apps'].get_model('users', 'User')
        Department = kwargs['apps'].get_model('users', 'Department')
    except LookupError:
        return

    username_number = 100000
    for department_name in settings.API_SETTINGS.DEFAULT_DEPATMENT:
        department = Department.objects.get(department_name=department_name)
        if User.raw_objects.filter(department=department).exists():
            break

        username_number += 1
        user, _ = User.raw_objects.get_or_create(
            department=department,
            username=str(username_number),
            defaults={
                'password': make_password(settings.API_SETTINGS.DEFAULT_USER_PASSWORD),
                'is_staff': False, 'is_superuser': False, 'is_leader': True
            }
        )

        username_number += 1
        user, _ = User.raw_objects.get_or_create(
            department=department,
            username=str(username_number),
            defaults={
                'password': make_password(settings.API_SETTINGS.DEFAULT_USER_PASSWORD),
                'is_staff': False, 'is_superuser': False, 'is_leader': False
            }
        )


class UsersConfig(AppConfig):
    """app配置"""
    name = 'users'
    verbose_name = '用户管理'

    def ready(self):
        """生成默认数据，迁移之后执行"""
        # post_migrate.connect(create_default_super_user, sender=self)
        # post_migrate.connect(create_default_department, sender=self)
        # post_migrate.connect(create_default_department_user, sender=self)
        pass
