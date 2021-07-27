"""消息数量统计数据存储

MetricsStorage: 存储接口，子类继承该父类实现不同的存储方式
RedisMetricsStorage: 使用redis存储统计数据
"""
import datetime

from redis import RedisError
from django_redis import get_redis_connection

from settings import settings
from utils.exceptions import StorageMsgMetricsError


class MetricsStorage:
    """存储接口"""

    def storage(self, collected_name):
        """子类重写该方法并实现具体的存储逻辑

        Args:
            collected_name: 子系统名称
        """
        raise NotImplementedError('method storage() must be Implemented.')


class RedisMetricsStorage(MetricsStorage):
    """redis存储

    class Attributes:
        EXPIRE_TIME: 数据1天后过期
        metrics_key_name: hash名称, {date}为当前日期  system_metrics_2021-04-12
    """
    cache_redis_conn = get_redis_connection('cache')
    EXPIRE_TIME = settings.REDIS_METRICS_EXPIRE_TIME
    metrics_key_name = 'system_metrics_{date}'

    @property
    def current_date(self):
        """获取当前日期"""
        if not hasattr(self, '_current_date'):
            self._current_date = datetime.datetime.now().date()

        return self._current_date

    def storage(self, collected_name):
        """存储数据到redis"""
        key_name = self.metrics_key_name.format(date=self.current_date)
        try:
            # 增加调用次数
            self.cache_redis_conn.hincrby(key_name, collected_name)

            # 增加数据有效期
            if self.cache_redis_conn.ttl(key_name) == -1:
                # 当 key不存在时，返回 -2:key不存在, -1: 没有设置剩余生存时间, 否则: 以秒为单位
                self.cache_redis_conn.expire(key_name, self.EXPIRE_TIME)
        except RedisError as exc:
            raise StorageMsgMetricsError(exc)
