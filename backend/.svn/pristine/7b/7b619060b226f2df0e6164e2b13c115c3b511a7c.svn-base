import time
import random
from paho.mqtt import publish


dev_li = [
    # '4D3D10EB-2EAB-4D6B-B03E-713B28C2B71B',
    # 'D5CF2240-15B0-4016-BCA3-5ABACA477AEA',
    # '3F06B919-5C84-4FCC-AC33-1AC4ADC8D419',
    'D32CFC4C-FEDC-42FD-BF04-1FBAD0FBA1E1',
]

def get_data():
    return {
        "msg":{
          "head":{
            "service_code":"RUC_AIS_ALARM_TRIGGER",
            "version":"1.0",
            "sender_platform":"RUC",
            "sender_sys":"AIS",
            "receiver_platform":"SMP",
            "receiver_sys":"",
            "session_id": time.time(),
            "time_stamp":"20171208140658867"
        },
        "body":{
            "device": {
                "device_code": random.choices(dev_li)[0],
                "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                "ip": "192.168.21.185",
                "port": 554,
                "areaName": "1"
            },
            "passenger":{
                'time': time.time(),
                'analyzerResult':{
                "areaName": random.choices(
                    [
                    'E01柜台',
                    'E02柜台',
                    'E03柜台',
                    'E04柜台',
                    'E05柜台',
                    'E06柜台',
                    'E07柜台',
                    'E08柜台',
                    'E09柜台',
                    'E10柜台',
                    'E11柜台',
                    'E12柜台',
                    '安检口01',
                    '安检口02',
                    '安检口03',
                    '安检口04',
                    '安检口05',
                    '安检口06',
                    '安检口07',
                    '安检口08',
                    '安检口09',
                    '安检口10',
                    ])[0],
                # "areaName": '安检口01',
                "areaNum": random.randint(0, 100)
            }}
        }
    }
    }


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    import json
    topic = 'zvams/analysis/queue/alarm'
    print(content)
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    publish_mq_message(get_data())
    time.sleep(5)
    # break

# 多线程 慢ws
# 1603086491.5605462
# 1603086518.010805
# 27


# 多线程 快ws
# start_time:1603086620.376298
# end_time:  1603086637.509912
# 17

# 单线程 快ws
# start_time:1603086919.276303
# end_time:  1603086934.889028
# 15

# 单线程 慢ws
# start_time:1603087060.12079
# end_time:  1603087085.015572
# 25

# start_time:1603087149.614599
# end_time:  1603087173.917542
# 24

# start_time: 1603087210.3599749
# end_time:   1603087237.113707

# start_time:1603087283.488086
# end_time:1603087308.614725
# # 25