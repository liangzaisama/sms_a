from django.apps import AppConfig
from django.db.models.signals import post_migrate

from scripts.create_default_data import CreateDefaultModelData


def create_default_situation_data(*args, **kwargs):
    """创建态势默认数据"""
    situation_models = ['ResourceInfo']

    for model_name in situation_models:
        CreateDefaultModelData('situations', model_name)(*args, **kwargs)


class SituationsConfig(AppConfig):
    """situations app配置"""
    name = 'situations'
    verbose_name = '态势管控'

    def ready(self):
        """接收到migrate信号时执行, 创建默认的态势资源"""
        # post_migrate.connect(create_default_situation_data, sender=self)
        pass
