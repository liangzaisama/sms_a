"""发送消息给esb航班系统的装饰器

SendIIS: 装饰器类
Examples:
     @SendIIS('SIP', 'REALTIMECHANNEL')
    def func()...
"""
from security_platform import receive_logger as logger

from esb import esb_send_msg_queue
from esb.esb_data_package import esb_msg_package
from utils.exceptions import RedisQueueError


class SendIIS:
    """发送消息给esb的装饰器

    Attributes:
        iis_type: 消息类型
        iis_son_type: 消息子类型
        func: 被装饰的函数
    """
    def __init__(self, iis_type, iis_son_type):
        self.iis_type = iis_type
        self.iis_son_type = iis_son_type
        self.func = None

    def run_func(self, label):
        """执行原始函数, 并将数据放到esb_send_msg_queue队列

        esb发送消息进程会从队列中拿走数据并发送

        Args:
            label: 子系统发送来的数据
        """
        result = self.func(self, label)
        data = esb_msg_package.package_analysis_data(self.iis_type, self.iis_son_type, label)

        try:
            esb_send_msg_queue.put(data)
        except RedisQueueError as exc:
            logger.error(exc)

        return result

        # try:
        #     esb_send_msg_queue.put_nowait(data)
        # except queue.Full:
        #     # 如果堵塞，就直接丢弃消息，保证业务逻辑正常的执行
        #     logger.warning('esb发送消息队列已满，丢弃消息')

    def __call__(self, func):
        self.func = func
        return self.run_func
