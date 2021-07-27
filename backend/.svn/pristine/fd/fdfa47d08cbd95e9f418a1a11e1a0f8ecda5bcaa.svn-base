import json

from redis import RedisError
from django_redis import get_redis_connection

from utils.exceptions import RedisQueueError


class RedisQueue:
    """
    适配器模式
    将redis的队列封装成跟python的Queue一样的方法，适配原实现的接口
    """
    def __init__(self, queue_name, redis_alias='queue', queue_max_count=5000):
        self.queue_name = queue_name
        self.queue_max_count = queue_max_count
        self.redis_conn = get_redis_connection(redis_alias)

    def len(self):
        return self.redis_conn.llen(self.queue_name)

    def put(self, data):
        """将消息放入队列，并维持队列数量不多于5000个

        保证队列大小不超过5000条,数据总是维持最新的,防止发送消息进程挂掉后,队列无限变大
        """
        try:
            self.redis_conn.lpush(self.queue_name, json.dumps(data).encode())
            self.redis_conn.ltrim(self.queue_name, 0, self.queue_max_count)
        except RedisError as exc:
            raise RedisQueueError('放入redis队列数据失败:%s', exc)

    def get(self):
        """从队列中获取数据，如果没数据则一直阻塞"""
        try:
            data = self.redis_conn.brpop(self.queue_name)
            return json.loads(data[1].decode())
        except RedisError as exc:
            raise RedisQueueError('获取redis队列数据失败:%s', exc)
