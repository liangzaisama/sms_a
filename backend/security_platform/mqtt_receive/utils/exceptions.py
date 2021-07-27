class CustomerException(Exception):
    """自定义根异常"""
    pass


class StorageMsgMetricsError(CustomerException):
    """存储消息指标数据"""
    pass


class MsgParseError(CustomerException):
    """mq消息字段解析失败"""
    pass


class InvalidMsgFiledError(CustomerException):
    """mq消息字段异常"""
    pass


class DuplicateError(CustomerException):
    """重复数据"""
    pass


class InvalidDeviceCodeError(CustomerException):
    """错误的设备编码"""
    pass


class NoProcessingError(CustomerException):
    """不处理消息"""
    pass


class RequestVASError(CustomerException):
    """请求人像库接口报错"""
    pass


class WebsocketError(CustomerException):
    """Websocket报错"""
    pass


class RedisQueueError(CustomerException):
    """redis队列异常"""
    pass
