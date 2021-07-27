"""MQ消息处理程序入口文件

main 入口函数，程序执行时调用此函数
ProcessManager 进程管理，负责消息处理worker和websocket进程连接的进程创建及监控

Examples:
    main()
"""
import os
import sys
import time

import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir))

try:
    from manage import set_django_module
    set_django_module()
    django.setup()

    from security_platform import config_parser, receive_logger as logger

    from settings import settings
    from proc import ProcessTypeEnum
    from utils.topic import SUBSCRIBE_TOPIC
    from core.client import callback, MessageQueueClient
except ImportError:
    raise ImportError("Couldn't import DJANGO_SETTINGS_MODULE")


class ProcessManager:
    """进程管理

    负责事件消息处理worker类和websocket连接的进程创建及监控
    """
    process_classes = settings.RUN_PROCESS_CLASSES

    def __init__(self):
        """初始化"""
        self._processes = []

    @property
    def process(self):
        """管理的进程列表"""
        return self._processes

    def create_process(self, process_class,  **kwargs):
        """创建进程

        创建进程并启动，添加到管理进程列表中

        Args:
            process_class: 进程类
            **kwargs: 初始化参数
        """
        process = process_class(daemon=True, **kwargs)
        process.kwargs = kwargs
        process.start()

        self._processes.append(process)

    def _register(self):
        """进程注册"""
        for process_class in self.process_classes:
            if process_class.get_process_type() != ProcessTypeEnum.MQ_WORKER:
                self.create_process(process_class)
            else:
                for registry in callback.registry_list:
                    callback_class = getattr(callback, registry.class_name)

                    if issubclass(callback_class, callback.MultiprocessMessageCallback):
                        # 只处理多进程消息worker
                        for _ in range(registry.process_count):
                            self.create_process(process_class, target=registry.worker(registry.queue).loop_forever)

    def _monitor(self):
        """子进程监控

        每5秒中执行依次，无限循环
        如果进程死亡，将新的进程添加到进程列表，将死亡的进程剔除
        """
        while True:
            copy_process = self._processes.copy()

            for process in copy_process:
                if not process.is_alive():
                    logger.error('die process %s', process)
                    process.terminate()

                    self.create_process(type(process), **process.kwargs)
                    self._processes.remove(process)

            time.sleep(settings.PROCESS_MONITOR_INTERVAL)

    def start(self):
        """启动函数"""
        self._register()
        self._monitor()


def main():
    """入口函数"""
    # 开启mq连接
    mq_client = MessageQueueClient(SUBSCRIBE_TOPIC, callback.registry_list)
    mq_client.connect(
        int(config_parser.get('MQTT', 'MQTT_PORT')),
        config_parser.get('MQTT', 'MQTT_SERVER_IP'),
        config_parser.get('MQTT', 'MQTT_USER'),
        config_parser.get('MQTT', 'MQTT_PWD')
    )

    # 创建消息处理进程
    ProcessManager().start()


if __name__ == '__main__':
    main()
