"""MQ连接客户端类

Examples:
    mq_client = MessageQueueClient(SUBSCRIBE_TOPIC, callback.registry_list)
    mq_client.connect(config.MQTT_PORT, config.MQTT_SERVER_IP, config.MQTT_USER, config.MQTT_PWD)
"""
import json
import time
import datetime

from paho.mqtt.client import Client, MQTT_ERR_SUCCESS, MQTT_ERR_CONN_LOST, time_func

from security_platform import receive_logger as logger

from core import callback
from utils import constants
from settings import settings


class CustomerClient(Client):

    @property
    def last_msg_timestamp(self):
        return getattr(self, '_last_msg_timestamp', None)

    @last_msg_timestamp.setter
    def last_msg_timestamp(self, value):
        self._last_msg_timestamp = value

    def reconnect(self):
        self.last_msg_timestamp = None
        return super().reconnect()

    def loop(self, *args, **kwargs):
        """增加接受消息超时判断

        如果上一条消息离现在超过一定时间, 则返回连接丢失
        """
        last_msg_timestamp = self.last_msg_timestamp

        if last_msg_timestamp is not None:
            # print(time_func() - last_msg_timestamp)
            if time_func() - last_msg_timestamp >= settings.reconnect_no_msg_time:
                logger.warning('超过%s秒未收到消息，执行重连', settings.reconnect_no_msg_time)
                return MQTT_ERR_CONN_LOST

        return super().loop(*args, **kwargs)


class GenericMessageQueueClient:
    """mq连接通用类

    调用connect方法连接MQ, 连接后自动回调到on_connect并订阅主题及发送初始化消息

    Attributes:
        subscribe_topic: 订阅主题列表
        callback_list: 消息回调列表，从回调类的注册列表中获取，列表中的元素是回调类相关信息的具名元组
        _client: 连接后的MQ连接对象

    Class Attributes:
        publish_classes: 连接初始化时发送的消息类, 通过该类的get_data方法获取要发送的数据
    """
    publish_classes = ()

    def __init__(self, subscribe_topic, callback_list=None):
        """初始化"""
        self.subscribe_topic = subscribe_topic
        self.callback_list = callback_list
        self._client = None

    def get_publish_classes(self):
        """获取发送消息类对象列表"""
        return [publish_class() for publish_class in self.publish_classes]

    def publish(self):
        """发送初始化的消息"""
        for publish_instance in self.get_publish_classes():
            publish_msg = json.dumps(publish_instance.get_publish_msg())
            logger.info('发送初始化消息:%s', publish_msg)
            self._client.publish(
                publish_instance.get_topic(),
                publish_msg,
                qos=constants.MQTT_QOS_LEVEL
            )

    def on_connect(self, *args):
        """连接MQ成功后的回调函数

        连接成功后订阅消息主题，发送初始化消息
        连接失败断开连接

        Args:
            *args: 回调相关参数
        """
        client, *_, rc = args
        if rc == MQTT_ERR_SUCCESS:
            logger.info(f'订阅主题:{self.subscribe_topic}')
            logger.info(f'订阅时间为:{datetime.datetime.now()}')
            client.subscribe(self.subscribe_topic, qos=constants.MQTT_QOS_LEVEL)

            time.sleep(1)
            self.publish()
        else:
            logger.error('连接错误，错误码%d 执行重连' % rc)
            time.sleep(1)
            client.reconnect()

    def add_callback(self):
        """增加回调函数"""
        for registry in self.callback_list:
            for topic in registry.topic:
                self._client.message_callback_add(topic, getattr(callback, registry.class_name).on_message)

    def connect(self, port, host, username, password):
        """连接MQ服务端

        Args:
            port: MQ端口
            host: MQ ip地址字符串
            username: MQ用户名字符串
            password: MQ密码字符串
        """
        self._client = CustomerClient(client_id=settings.MQ_CLIENT_ID)
        self._client.max_inflight_messages_set(settings.MAX_INFLIGHT_MESSAGES_SET)
        self._client.username_pw_set(username, password)
        self._client.on_connect = self.on_connect
        self._client.connect_async(host, port=port, keepalive=65535)
        self._client.loop_start()
        self.add_callback()


class MessageQueueClient(GenericMessageQueueClient):
    """mq连接类

    连接成功后发送初始化航班基础请求数据
    """
    publish_classes = settings.MQ_PUBLISH_CLASSES
