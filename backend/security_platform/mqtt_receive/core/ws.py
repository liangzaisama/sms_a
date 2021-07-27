"""webscoket连接相关处理

ws_connections：websocket连接池，根据不同的连接地址获取不同的连接，且每个进程之前的连接相互独立

Examples:
    conn = ws_connections['ws://127.0.0.1:8888/ws/event']
"""
import time
import socket
from threading import local

from websocket import create_connection, WebSocketException

from security_platform import receive_logger as logger

from utils.common import time_consuming
from utils.exceptions import WebsocketError


class WebsocketConnectionWrapper:
    """websocket连接包装器

    Attributes:
        connection: 当前websocket连接
        ws_url: 当前websocket连接地址
        max_age: websocket连接持久时间
        close_at: 当前websocket连接关闭时间
    """

    def __init__(self, ws_url):
        """初始化

        Args:
            ws_url: websocket连接地址
        """
        self.connection = None
        self.ws_url = ws_url
        self.max_age = 3600
        self.close_at = None

    def connect(self):
        """连接websocket

        连接成功后设置连接的关闭时间, layer阻塞时可能会很久，所以建议使用异步执行websocket

        Raises:
            WebsocketError: 连接失败时抛出异常
        """
        try:
            self.connection = create_connection(self.ws_url, timeout=self.max_age)
        except (ConnectionError, socket.error, WebSocketException) as exc:
            raise WebsocketError(f'连接websocket失败 ws_url:{self.ws_url} error:{exc}')
        else:
            self.close_at = time.time() + (self.max_age - 30)

    def close(self):
        """关闭连接"""
        if self.connection is not None:
            try:
                self.connection.close()
            except:
                pass
            finally:
                self.connection = None

    def reconnect_if_obsolete(self):
        """超时重连"""
        if self.connection is not None:
            if self.close_at is not None and time.time() >= self.close_at:
                self.close()
                self.connect()

    def ensure_connection(self):
        """确保存在连接"""
        if self.connection is None:
            self.connect()

    def __enter__(self):
        """with调用时返回连接"""
        self.reconnect_if_obsolete()
        self.ensure_connection()

        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """发送异常时关闭连接"""
        if exc_type is None:
            return None

        logger.error('发送websocket消息失败:%s', exc_val)

        self.close()
        return True


class WebsocketConnectionHandler:
    """连接中介

    Attributes:
        _connections: websocket连接池，存储了不同进程使用的连接对象
    """

    def __init__(self):
        self._connections = local()

    def __getitem__(self, ws_url):
        """通过websocket地址获取连接

        实际是从自身维护的连接池中获取连接，如果没有连接则创建一个新的返回

        Args:
            ws_url: websocket连接地址

        Returns:
            跟地址对应的ws连接对象

        Examples:
            conn = ws_connections['event']
        """
        if hasattr(self._connections, ws_url):
            return getattr(self._connections, ws_url)

        conn = WebsocketConnectionWrapper(ws_url)
        setattr(self._connections, ws_url, conn)
        return conn

    def __setitem__(self, key, value):
        """设置连接到连接池"""
        setattr(self._connections, key, value)

    def __delitem__(self, key):
        """连接池中删除连接"""
        delattr(self._connections, key)


ws_connections = WebsocketConnectionHandler()
