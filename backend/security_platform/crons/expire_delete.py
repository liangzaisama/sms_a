"""删除历史的视频分析数据

每天执行一次

当前删除策略：
报警事件：1年
子系统事件：1年
视频分析实时事件：60天
视频分析报警事件：60天
"""
from itertools import islice
from datetime import datetime, timedelta

from django_setup import logger, event_model, SystemConfig, FlightInfo, PassageWayCarPassThrough, redis_lock_factory


class GenericModelDeleter:
    """数据删除器

    子类可继承该类，修改model_classes和expire_config_name来设置删除的模型类和数据的过期时间配置

    class Attributes:
        model_classes: 要删除的模型类，子类将要删除的模型类放到其中
        expire_config_name: 关联配置名称，可根据配置名称在配置中查到对应的数据过期配置值
    """

    model_classes = ()
    expire_config_name = None

    def get_config_name(self):
        """获取数据过期时间的配置名称，根据配置名称获取配置表中对应的数据过期时间

        Raises:
            AssertionError: 子类未定义expire_config_name时抛出异常
        """
        assert self.expire_config_name is not None, (
                "'%s' should either include a `config_key` attribute, "
                "or override the `get_config_name()` method." % self.__class__.__name__
        )
        return self.expire_config_name

    def get_expire_time(self):
        """获取数据过期时间"""
        return datetime.now() - timedelta(days=SystemConfig.objects.get(config_key=self.get_config_name()).value)

    def delete(self):
        """根据过期时间, 执行数据删除

        每天执行一次，当天的数据量不会太大
        """
        for model in self.model_classes:
            objs = model.objects.filter(create_time__lt=self.get_expire_time())

            while True:
                batch = list(islice(objs, 100000))
                if not batch:
                    break

                delete_info = objs.delete()
                logger.info('删除数据:%s', delete_info)


class AlarmEventDeleter(GenericModelDeleter):
    """报警事件删除器"""
    model_classes = [event_model.AlarmEvent]
    expire_config_name = SystemConfig.ConfigKey.EVENT_DELETE


class SubsystemCurrentEventDeleter(GenericModelDeleter):
    """子系统实时事件删除器"""
    model_classes = [FlightInfo, PassageWayCarPassThrough]
    expire_config_name = SystemConfig.ConfigKey.SUBSYSTEM_CURRENT


class AnalysisAlarmEventDeleter(GenericModelDeleter):
    """视频分析报警事件删除器"""
    model_classes = [
        event_model.DeployAlarmRecord,
        event_model.PersonDensityRecord,
        event_model.BehaviorAlarmRecord,
        event_model.PostureAlarmRecord,
        event_model.PlaceAlarmRecord,
    ]
    expire_config_name = SystemConfig.ConfigKey.ANALYSIS_ALARM


class AnalysisCurrentEventDeleter(GenericModelDeleter):
    """视频分析实时事件删除器"""
    model_classes = [
        event_model.DeployPersonSnapRecord,
        event_model.PeopleCountingRecord,
        event_model.PlaceSafeguardRecord,
    ]
    expire_config_name = SystemConfig.ConfigKey.ANALYSIS_CURRENT


class Main:
    """删除器应用类"""

    # 要执行的删除器
    deleter_classes = [
        AlarmEventDeleter,
        # SubsystemCurrentEventDeleter,
        # AnalysisAlarmEventDeleter,
        # AnalysisCurrentEventDeleter,
    ]

    def get_deleter(self):
        """获取删除器对象

        Returns:
            删除器对象列表
        """
        return [deleter() for deleter in self.deleter_classes]

    @redis_lock_factory('delete_expire_data', 3600)
    def __call__(self, *args, **kwargs):
        """调用删除器删除数据"""
        for deleter in self.get_deleter():
            deleter.delete()


delete_expire_data = Main()


if __name__ == '__main__':
    delete_expire_data()
