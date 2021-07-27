import random

from paho.mqtt import publish
import uuid


li = [
    '8A6DD6A7-DE84-40C4-B4F7-1D62A27E3148',
    # '644CC4DB-D0FE-4FAC-BC12-A299E0F28BFC',
    # '547439F2-9C14-474C-9246-844E36ADF479'
]

status = {
	"msg": {
		"head": {
	            "service_code":"SMP_ACS_DEVICE_ADD",
                "version":'1.0',
                "sender_platform":"SMP",
                "sender_sys":"ACS",
                "receiver_platform":"",
                "receiver_sys":"",
                "session_number":"",
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
		    },
		"body": {
			  "device_status": {
                  "device_code":random.choices(li)[0],
                  "device_state":'normal',
                  "error_code":'1',
                  "error_message":'设备损坏',
			    }
		}
	}
}

# camera = 'VMS', '视频监控系统'
# maintenance = 'AIS', '围界系统'
# entrance = 'ACS', '门禁系统'
# fire = 'XFHZ', '消防系统'
# conceal = 'YBBJ', '隐蔽报警系统'
# passage = 'CMS', '道口系统'


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    import json
    topic = 'vms/device/statechange'
    publish.single(topic, json.dumps(content), qos=1, hostname='10.129.137.33',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    time.sleep(2)
    publish_mq_message(status)
