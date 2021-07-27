from django.apps import AppConfig
from django.db.models.signals import post_migrate

from scripts.create_default_data import CreateDefaultModelData


def create_default_system_config(**kwargs):
    """创建默认系统配置数据"""
    from configurations.models import SystemConfig
    SystemConfig.config_data_init()


def create_default_gis_info(*args, **kwargs):
    """创建态势默认数据"""
    gis_models = ['GisMap', 'GisLayer']

    for model_name in gis_models:
        CreateDefaultModelData('configurations', model_name)(*args, **kwargs)


class ConfigurationsConfig(AppConfig):
    name = 'configurations'
    verbose_name = '系统配置'

    def ready(self):
        post_migrate.connect(create_default_system_config, sender=self)
        post_migrate.connect(create_default_gis_info, sender=self)
