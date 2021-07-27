"""esb发送消息进程

send_msg_to_esb: 进程启动跳用函数，从进程队列esb_send_msg_queue中获取数据并发送到esb
"""
import time
from threading import Thread

from security_platform import receive_logger as logger

from settings import settings
from core.worker import EsbPublishWorker
from utils.exceptions import RedisQueueError
from esb import esb_send_msg_queue
from esb.esb_data_package import esb_msg_package


class EsbInitPublishMsgThread(Thread):
    """初始化消息执行线程"""

    def run(self):
        """将初始化消息放到队列，定时放，因为esb有发送间隔限制"""
        for data in esb_msg_package.initial_request_data:
            try:
                esb_send_msg_queue.put(data)
            except RedisQueueError as exc:
                logger.error(exc)
            else:
                time.sleep(settings.ESB_SEND_FREQUENCY)


def send_msg_to_esb():
    """发送数据到esb"""

    # 发送基础请求事件
    EsbInitPublishMsgThread().start()

    # 开始处理给航班系统发送的额消息
    EsbPublishWorker(esb_send_msg_queue).loop_forever()
