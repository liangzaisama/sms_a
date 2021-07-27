"""esb接受消息进程执行函数

receive_msg_from_esb：进程运行函数
"""
from jpype import JClass

from core.worker import EsbReceiveWorker
from security_platform import receive_logger as logger


def receive_msg_from_esb():
    """调用esb的java sdk获取esb的消息"""
    esb_consumer_with_auto_ack = JClass("com.caacitc.consumer.EsbConsumerWithAutoAck")()
    # 获取消息存储队列
    java_block_queue = esb_consumer_with_auto_ack.getListenerImplTest().getQueue()
    # 启动接收消息服务
    esb_consumer_with_auto_ack.main([])

    # 连接成功状态码
    success_connect_code = '0'
    connect_code = esb_consumer_with_auto_ack.getConnectCode()

    if connect_code == success_connect_code:
        # 连接航班系统MQ成功
        logger.info('航班系统消费者启动成功:%s', connect_code)
        EsbReceiveWorker(java_block_queue).loop_forever()
    else:
        logger.error('航班系统消费者启动失败:%s', connect_code)
