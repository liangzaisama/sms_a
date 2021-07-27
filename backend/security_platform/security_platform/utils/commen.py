"""
提供工具函数
"""
import datetime

from paho.mqtt import publish
from django_redis import get_redis_connection

from security_platform import config_parser


def get_redis_lock(lock_key, expire):
    """基于redis实现的分布式锁

    分布式环境下并发使用

    Args:
        lock_key: 锁名称
        expire: 锁过期时间，保证了过期时间内不锁不释放，无法重复调用

    Returns:
        获取锁成功时返回1
        获取锁失败时返回0
    """
    redis_conn = get_redis_connection('lock')
    return redis_conn.set(lock_key, 'lock_key', ex=expire, nx=True)


def redis_lock_factory(lock_key, expire):
    def redis_lock_decorate(func):
        def wrapper(*args, **kwargs):
            result = get_redis_lock(lock_key, expire)

            if result:
                # 获取锁成功，执行
                return func(*args, **kwargs)
            # else:
            #     print('获取锁失败，不执行')

        return wrapper
    return redis_lock_decorate


def datetime_to_str(date_time, date_format='%Y-%m-%d %H:%M:%S'):
    """datetime转格式化字符串"""
    if date_time is None:
        return date_time
    return datetime.datetime.strftime(date_time, date_format)


def blank_get(dict_obj, key):
    """如果字典对应的key值为None, 将其转化为空字符串

    Args:
        dict_obj: 字典对象
        key: 获取键字符串

    Returns:
        value: 返回值
    """
    value = dict_obj.get(key, '')
    if value is None:
        return ''

    return value


def iterable_to_str_tuple(iterable):
    """将可迭代对象转化为字符串带括号的格式

    为了方便使用原生sql的in查询时使用

    Args:
        iterable: 要转化的可迭代对象

    Returns:
        value: 转化后的字符串
        Examples：
            (1,2,3) -> '(1,2,3)'
            (1,) -> '(1)'
    """
    if len(iterable) == 1:
        return f'({iterable[0]})'

    return str(tuple(iterable))


def publish_message(topic, payload):
    """使用短连接发送MQ消息，发送完毕关闭MQ连接

    Args:
        topic: 消息主题
        payload: 消息内容
    """
    publish.single(
        topic,
        payload,
        qos=1,
        hostname=config_parser.get('MQTT', 'MQTT_SERVER_IP'),
        auth={
            'username': config_parser.get('MQTT', 'MQTT_USER'),
            'password': config_parser.get('MQTT', 'MQTT_PWD')
        }
    )


# class CRotatingFileHandler(RotatingFileHandler):
#
#     def emit(self, record):
#         log_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'logs')
#         if 'doRollover' in os.listdir(log_path):
#             self.doRollover()
#             os.remove(os.path.join(log_path, 'doRollover'))
#
#         return super().emit(record)
