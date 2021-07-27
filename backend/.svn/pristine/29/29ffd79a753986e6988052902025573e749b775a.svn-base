"""MQ订阅主题消息回调类

回调类定义时通过元类自动注册相关信息，并加入列表registry_list
"""
import queue
from collections import namedtuple

from django_redis import get_redis_connection

from security_platform import receive_logger as logger

from utils import topic
from settings import settings
from core import worker, Queue

registry_list = []
Registry = namedtuple('Registry', ['topic', 'class_name', 'queue', 'process_count', 'worker'])
redis_conn = get_redis_connection()


class RegisterMeta(type):
    """回调类元类

    将回调类的相关信息生成一个具名元组 Registry
    """

    def __new__(mcs, name, bases, class_dict):
        """回调类创建前注册信息"""
        mcs.registry_class(name, class_dict)
        return super().__new__(mcs, name, bases, class_dict)

    @staticmethod
    def registry_class(class_name, class_dict):
        """将回调类的具名元组信息添加到全局注册列表

        Args:
            class_name: 回调类的字符串名称
            class_dict: 回调类的属性字典
        """
        sub_topic = class_dict['topic']

        if sub_topic:
            registry_list.append(Registry(
                sub_topic, class_name, class_dict.get('queue'),
                class_dict.get('process_count'), class_dict.get('worker')
            ))


class RegisterAbstractMessageCallback(metaclass=RegisterMeta):
    """抽象MQ消息回调类

    Class Attributes:
        topic: 回调类关联的主题列表
    """
    topic = []

    @classmethod
    def handle(cls, *args):
        raise NotImplementedError('method handle() must be Implemented.')

    @classmethod
    def on_message(cls, *args):
        """消息回调时调用的函数, 赋值消息的时间戳给client对象"""
        client, _, msg = args
        client.last_msg_timestamp = msg.timestamp

        cls.handle(*args)


class MultiprocessMessageCallback(RegisterAbstractMessageCallback):
    """多进程消息回调

    通过on_message方法将对应的消息扔到队列交给worker处理

    Class Attributes:
        topic: 回调类关联的主题列表
        worker: 处理消息的类，worker从队列中取消息进行处理
        queue: 进程消息队列，收到的消息仍到该队列中
        process_count: 开启处理消息的进程个数，当消息数量较多时可增大进程数，增加处理能力
    """
    topic = []
    worker = None
    queue = None
    process_count = 0

    @classmethod
    def handle(cls, *args):
        """拿到消息后，将消息放到进程消息队列"""
        msg = args[-1]

        try:
            cls.queue.put_nowait((msg.topic, msg.payload.decode()))
        except queue.Full:
            # 熔断机制：一旦阻塞，就直接丢弃消息，保证业务逻辑正常的执行，防止MQ堵塞崩溃
            logger.error('MQ消息队列已满，丢弃消息, 请增加消息处理进程！')

        # try:
        #     cls.queue.put((msg.topic, msg.payload.decode()))
        # except RedisQueueError as exc:
        #     logger.error(exc)
        # s = time.perf_counter()


# class FlightMessageCallback(MultiprocessMessageCallback):
#     """航班系统消息回调"""
#
#     topic = [topic.IIS_SUBSCRIBE_TOPIC]
#     worker = worker.IISWork
#     queue = Queue(100)
#     process_count = 1


class ACSCMSCallback(MultiprocessMessageCallback):
    """门禁/道口消息回调"""

    topic = [
        topic.CMS_SUBSCRIBE_TOPIC,
        topic.ACS_SUBSCRIBE_TOPIC,
    ]
    worker = worker.ACSCMSCallWork
    # queue = RedisQueue('ACSCMSQueue')
    queue = Queue(settings.QUEUE_LENGTH)
    process_count = 1


class CommonMessageMaintenanceCallback(MultiprocessMessageCallback):
    """分析/监控/消防/防隐蔽报警/围界消息回调"""

    topic = [
        topic.VMS_SUBSCRIBE_TOPIC,
        # topic.CMS_SUBSCRIBE_TOPIC,
        # topic.ACS_SUBSCRIBE_TOPIC,
        topic.YBBJ_SUBSCRIBE_TOPIC,
        topic.AIS_SUBSCRIBE_TOPIC,
        topic.XFHZ_SUBSCRIBE_TOPIC,
        topic.ZVAMS_SUBSCRIBE_TOPIC,
    ]
    worker = worker.CommonWork
    # queue = RedisQueue('CommonQueue')
    queue = Queue(settings.QUEUE_LENGTH)
    process_count = settings.CommonMessageProcessCount
