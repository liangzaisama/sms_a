import time
import random
from paho.mqtt import publish

dev_li = [
    # '4D3D10EB-2EAB-4D6B-B03E-713B28C2B71B',
    # 'D5CF2240-15B0-4016-BCA3-5ABACA477AEA',
    # '3F06B919-5C84-4FCC-AC33-1AC4ADC8D419',
    '0C70CF77-A374-4503-B9B6-C246F82FCDA4',
]


def get_data(session_id):
    return {
        "msg":{
          "head":{
            "service_code":"RUC_AIS_ALARM_TRIGGER",
            "version":"1.0",
            "sender_platform":"RUC",
            "sender_sys":"AIS",
            "receiver_platform":"SMP",
            "receiver_sys":"",
            "session_id":session_id,
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
                "time": time.time(),
                'analyzerResult': {
                    "alarmLevel": random.randint(0, 3),
                    "areaNum": random.randint(0, 100)
                },
            "densityImage": 'http://192.168.21.150/media/alarm/20210107103408065900/daa4abda-5094-11eb-be80-3448edf59a40.jpg',
            }
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
    topic = 'zvams/analysis/people/density'
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    time.sleep(1)
    publish_mq_message(get_data(time.time()))
    # break
