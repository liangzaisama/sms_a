"""消息处理worker类

不同进程通过不同worker来处理消息, worker通过loop_forever方法获取队列中的消息进行处理
"""
import hashlib
import os
import time
from pyexpat import ExpatError
from json import JSONDecodeError, loads
from concurrent.futures.thread import ThreadPoolExecutor

import xmltodict
import dicttoxml
from jpype import JClass
from jpype._core import JVMNotRunning

from security_platform import receive_logger as logger

from core import mixins
from core.storage import RedisMetricsStorage
from security_platform.utils.commen import get_redis_lock
from settings import settings
from utils.topic import PERSON_SNAP_TOPIC_PREFIX
from utils.exceptions import CustomerException, MsgParseError, StorageMsgMetricsError


class GenericWorker:
    """通用worker处理

    Attributes:
        queue: worker获取消息处理的进程消息队列
    """
    def __init__(self, queue):
        self.queue = queue
        self.thread_pool = ThreadPoolExecutor(4)

    def handler_not_found(self, _):
        """消息不需要处理时调用"""
        pass
        # logger.debug('不处理的消息')

    def _dispatch(self, msg):
        try:
            self.dispatch(msg)
        except CustomerException as exc:
            # 消息处理内部抛出的异常信息
            logger.warning(exc, exc_info=False)
        except Exception as exc:
            # 未捕获到的异常信息
            logger.error('消息处理异常:%s', exc, exc_info=True)

    def dispatch(self, msg):
        """消息分配处理

        通过消息内容获取要处理的函数名称并调用对应的函数，找不到对应函数名称时调用handler_not_found函数

        Args:
            msg: 要处理的消息字符串
        """
        logger.debug('进程:%s worker:%s 接收消息为:%s', os.getpid(), self.__class__, msg)
        dict_msg = self.parse_msg_to_dict(msg)
        handler_name = self.get_msg_handler_name(dict_msg)
        msg_handler = self.get_msg_handler(handler_name)
        msg_handler(dict_msg)
        # response = msg_handler(dict_msg)
        # print(response)

    def parse_msg_to_dict(self, msg):
        """子类需继承方法并实现将消息格式转为字典的逻辑

        Args:
            msg: 消息字符串格式

        Returns：
            消息的字典格式
        """
        raise NotImplementedError('method parse_data() must be Implemented.')

    def get_msg_handler_name(self, msg):
        """获取消息对应的执行函数

        Args:
            msg: 消息字符串格式

        Returns:
            处理消息的函数名
        """
        raise NotImplementedError('method get_msg_handler_name() must be Implemented.')

    def get_msg_handler(self, handler_name):
        """根据函数名称获取函数对象

        找不到时返回handler_not_found函数，跳过消息处理

        Args:
            handler_name: 函数名称

        Returns:
            函数对象
        """
        return getattr(self, handler_name, self.handler_not_found)

    def get_msg(self):
        """从队列中获取消息，没消息时会卡住"""
        return self.queue.get()

    def loop(self):
        """获取消息并处理"""
        msg = self.get_msg()

        # 使用线程执行、防止阻塞
        self.thread_pool.submit(self._dispatch, msg)

    # noinspection PyBroadException
    def loop_forever(self):
        """循环处理队列中的消息"""
        while True:
            try:
                self.loop()
            except (RuntimeError, JVMNotRunning, BrokenPipeError, EOFError):
                # 程序退出时抛出的异常
                pass
            except Exception as exc:
                logger.error('消息处理异常:%s', exc)


class MetricsCollectorGenericWorker(GenericWorker):
    """消息统计worker"""

    belong_system = None
    metrics_storage = RedisMetricsStorage()

    def __init__(self, *args, **kwargs):
        self.storage_msg = None
        super().__init__(*args, **kwargs)

    def get_belong_system(self):
        """获取系统名称"""
        assert self.belong_system is not None, (
                "'%s' should either include a `belong_system` attribute, "
                "or override the `get_belong_system()` method." % self.__class__.__name__
        )

        return self.belong_system

    def logger_error(self, exc, exc_info=False):
        """打印错误"""
        logger.error('保存消息调用次数失败', exc, exc_info=exc_info)

    def storage(self):
        """执行存储"""
        try:
            self.metrics_storage.storage(self.get_belong_system())
        except (StorageMsgMetricsError, AssertionError) as exc:
            # redis存储失败或函数调用或配置失败
            self.logger_error(exc)
        except Exception as exc:
            # 未获取到的异常信息
            self.logger_error(exc, exc_info=True)

    def handler_not_found(self, _):
        """不处理消息不记录"""
        self.storage_msg = False
        super().handler_not_found(_)

    def dispatch(self, msg):
        """
        统计代码占用时间约:0.0002-0.0005, 基本无影响
        人数统计：0.0148-0.016 76路
        排队人数：0.014-0.028  143路 20s一轮
        人群密度：0.013-0.028  2路
        姿态动作：0.013-0.021  2路
        人脸抓拍：0.011-0.026  100路 一天10w, 60天600w
        人脸报警：0.012-0.018  100路 报警略少
        机位检测：0.012-0.018  18路
        舱门检测：0.012-0.018  18路
        道口车辆：0.008-0.019
        围界报警：0.022-0.034
        """
        self.storage_msg = True
        super().dispatch(msg)

        if self.storage_msg:
            self.storage()


class TopicWorker(MetricsCollectorGenericWorker):
    """MQ消息处理"""

    def __init__(self, *args, **kwargs):
        self.topic = None

        super().__init__(*args, **kwargs)

    def get_belong_system(self):
        assert self.topic is not None, (
            'please set a `topic` instance attribute before call method get_belong_system()'
        )
        return self.topic.split('/')[0]

    def parse_msg_to_dict(self, msg):
        self.topic = msg[0]

        try:
            dict_msg = loads(msg[1])
        except JSONDecodeError as exc:
            raise MsgParseError(f'json数据解析失败:{exc}')

        return dict_msg

    def get_msg_handler_name(self, dict_msg):
        msg_topic = self.topic

        if msg_topic.startswith(PERSON_SNAP_TOPIC_PREFIX):
            # 抓拍主题
            msg_topic = PERSON_SNAP_TOPIC_PREFIX

        return msg_topic.lower().replace('/', '_')


class DistributedTopicWorker(TopicWorker):
    """分布式环境下TopicWorker类

    增加处理消息之前先将消息进行md5, 然后根据md5码获取对应的锁
    如果获取到锁则处理该条消息，如果未获取到锁，则不处理消息
    """
    MSG_LOCK_EXPIRE_TIME = 60 * 5  # 5分钟后锁自动消失

    def msg_to_md5(self, msg):
        m = hashlib.md5()
        m.update(msg.encode())
        return m.hexdigest()

    def dispatch(self, msg):
        """增加分布式锁，锁耗时大概0.0003秒"""
        # s = time.perf_counter()
        if get_redis_lock(self.msg_to_md5(msg[1]), self.MSG_LOCK_EXPIRE_TIME):
            # 获取锁成功，处理该消息
            logger.debug('获取锁成功，处理该消息')
            super().dispatch(msg)
        else:
            logger.debug('获取锁失败，不处理消息')

        # e = time.perf_counter()
        # print('dis', e-s)


class EsbReceiveWorker(MetricsCollectorGenericWorker,
                       mixins.IISBasicResourceMixin,
                       mixins.IISFlightMixin):
    """接收航班消息处理"""
    belong_system = 'iis'

    def parse_msg_to_dict(self, msg):
        try:
            return xmltodict.parse(str(msg))
        except ExpatError as exc:
            raise MsgParseError(f'xml数据解析失败:{exc}')

    def get_msg_handler_name(self, dict_msg):
        return f"iis_{dict_msg['MSG']['META']['STYP'].lower()}"

    def get_msg(self):
        return self.queue.take()


class EsbPublishWorker(MetricsCollectorGenericWorker):
    """发送航班消息处理

    使用redis队列，因为esb同时只允许一个登陆，所以分布式情况下，只有一台配了esb发送消息
    的进程，可通过redis队列来获取发送的消息
    """

    # 不限制频率的消息
    ignore_frequency_msg_types = ()
    # worker归属系统
    belong_system = 'iis_publish'

    def __init__(self, *args, **kwargs):
        # 消息发送时间
        self.last_msg_send_timestamp = 0
        # 消息发送序号
        self.publish_sequence = 1

        super().__init__(*args, **kwargs)

    def dict_to_xml(self, dict_data):
        """将字典数据转为xml数据

        Args:
            dict_data: 需要转换的字典数据

        Returns:
            xml_data: 字典转换后xml数据
        """
        return dicttoxml.dicttoxml(dict_data, custom_root="MSG", attr_type=False).decode()

    def is_send_msg(self, msg):
        """发送频率限制"""
        current_timestamp = time.time()
        if msg['META']['STYP'] in self.ignore_frequency_msg_types:
            # 不限制发送频率的消息
            is_send = True
        else:
            is_send = (time.time() - self.last_msg_send_timestamp) >= settings.ESB_SEND_FREQUENCY

        if is_send:
            self.last_msg_send_timestamp = current_timestamp

        return is_send

    def msg_extra_process(self, msg):
        """消息额外处理"""
        msg['META']['SEQN'] = self.publish_sequence
        self.publish_sequence += 1

        return self.dict_to_xml(msg)

    def send_msg(self, msg):
        """连不上会卡顿10s"""
        producer = self.esb_client.getInstance.producer(msg)
        logger.debug(f'发送航班系统消息 {msg}')
        logger.debug(f'发送航班系统消息完成 code:{producer.getSendState()}, msg:{producer.getSendDesc()}')

    def _set_esb_client(self):
        self._esb_client = JClass("com.caacitc.rabbitmq.client.EsbClient")

    @property
    def esb_client(self):
        if not hasattr(self, '_esb_client'):
            self._set_esb_client()

        return self._esb_client

    def get_msg(self):
        """从队列中获取消息，没消息时会卡住"""
        return self.queue.get()

    def dispatch(self, msg):
        if self.is_send_msg(msg):
            self.send_msg(self.msg_extra_process(msg))
            self.storage()


# class VMSWork(TopicWorker, mixins.VMSMixin):
#     pass


class ACSCMSCallWork(DistributedTopicWorker,
                     mixins.PassCardMixin,
                     mixins.EntranceMixin,
                     mixins.PassageWayMixin):
    pass


class CommonWork(DistributedTopicWorker,
                 mixins.VideoAnalysisMixin,
                 mixins.MaintenanceMixin,
                 # mixins.EntranceMixin,
                 # mixins.PassCardMixin,
                 mixins.FireMixin,
                 mixins.ConcealMixin,
                 # mixins.PassageWayMixin,
                 mixins.ParkMixin,
                 mixins.IISFlightMixin,
                 mixins.CameraMixin):
    """围界/门禁/消防/隐蔽报警/道口/停车场/视频监控事件处理"""
    pass
