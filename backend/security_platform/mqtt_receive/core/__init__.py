from multiprocessing import Manager

Queue = Manager().Queue

# 1w条消息大约占内存1.6M
# 存储发送给esb消息的消息队列
# esb_send_msg_queue = Queue(settings.QUEUE_LENGTH)
