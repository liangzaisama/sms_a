from utils.constants import MQTT_QOS_LEVEL

# 服务状态检测主题
RECEIVE_SERVER_CHECK_TOPIC = 'smp/mq_check'

# 发送给航班系统的主题
PUBLISH_IIS_TOPIC_PREFIX = 'smp/iis/'

# 视频分析系统订阅主题
ZVAMS_SUBSCRIBE_TOPIC = 'zvams/#'

# 视频监控订阅主题
VMS_SUBSCRIBE_TOPIC = 'vms/#'

# 航班订阅主题
IIS_SUBSCRIBE_TOPIC = 'iis/#'

# 门禁订阅主题
ACS_SUBSCRIBE_TOPIC = 'acs/#'

# 通道订阅主题
CMS_SUBSCRIBE_TOPIC = 'cms/#'

# 围界订阅主题
AIS_SUBSCRIBE_TOPIC = 'ais/#'

# 消防订阅主题
XFHZ_SUBSCRIBE_TOPIC = 'xfhz/#'

# 隐蔽报警订阅主题
YBBJ_SUBSCRIBE_TOPIC = 'ybbj/#'

# 停车场
PARK_SUBSCRIBE_TOPIC = 'ps/#'

# 人脸抓拍主题前缀
PERSON_SNAP_TOPIC_PREFIX = 'zvams/face/capture'

# 统一订阅主题
SUBSCRIBE_TOPIC = [
    # 视频分析
    (ZVAMS_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 视频监控
    (VMS_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 航班
    (IIS_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 门禁，数据量大
    (ACS_SUBSCRIBE_TOPIC, 0),
    # 通道口
    (CMS_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 消防
    (XFHZ_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 隐蔽报警
    (YBBJ_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 围界
    (AIS_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 停车场
    (PARK_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
    # 航班
    # (IIS_SUBSCRIBE_TOPIC, MQTT_QOS_LEVEL),
]
