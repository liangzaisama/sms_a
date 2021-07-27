import socket

from rest_framework.settings import APISettings

from security_platform import config_parser


DEFAULTS = {
    # 多久内收不到消息,就自动重连,默认半小时
    'reconnect_no_msg_time': 60 * 30,
    # 消息处理进程个数
    'CommonMessageProcessCount': 8,
    # 消息队列长度
    'QUEUE_LENGTH': 5000,
    # 消息进程监控频率
    'PROCESS_MONITOR_INTERVAL': 5,
    # 消息统计存储时间
    'REDIS_METRICS_EXPIRE_TIME': 60 * 60 * 24,
    # esb发送消息频率 10s一条消息
    'ESB_SEND_FREQUENCY': 10,
    # esb初始化请求消息类型
    'ESB_INITIAL_REQUEST_CODES': (
        'RQAP',  # 机场
        'RQAR',  # 航班异常
        'RQAW',  # 航空公司
        'RQGT',  # 登机门
        'RQST',  # 机位
        'RQBL',  # 行李转盘
        'RQCC',  # 值机柜台
        'RQDF',  # 航班
    ),
    # MQ客户端id
    'MQ_CLIENT_ID': f'SMP1000-{config_parser.get("MQTT", "MQTT_USER")}-prod-{socket.gethostbyname(socket.gethostname())}',
    # 每次从rabbitmq取消息的数量、将存储在内存中、可以增大吞吐量
    'MAX_INFLIGHT_MESSAGES_SET': 200,
    # 初始化消息类
    'MQ_PUBLISH_CLASSES': (
        'utils.basicrequest.ACSPublishData',
        'utils.basicrequest.CMSPublishData',
        'utils.basicrequest.AccessCardPublishData',
    ),
    # 运行消息进程类型
    'RUN_PROCESS_CLASSES': (
        'proc.EsbReceiveProcess',
        'proc.EsbPublishProcess',
        'proc.MsgWorkerProcess',
    ),
}

IMPORT_STRINGS = (
    'MQ_PUBLISH_CLASSES',
    'RUN_PROCESS_CLASSES',
)

settings = APISettings(defaults=DEFAULTS, import_strings=IMPORT_STRINGS)
