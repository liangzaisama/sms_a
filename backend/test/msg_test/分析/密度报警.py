import time
import random
from paho.mqtt import publish


def test(hostname='127.0.0.1', sep=30, port=1883):
    dev_li = [
        '69D25210-AADA-4E22-A8FD-1CED20749475',
        '02FAB9A8-4165-4952-87E8-A9E2B45A65A8',
    ]

    image_li = [
        'http://192.168.21.150/media/alarm/20210401132004987697/1bfb31dc-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/1f023ae2-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/2206d630-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/253429ac-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/2844087e-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/2b5da402-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/2e7a901e-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/313c4078-969c-11eb-8891-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/31893c06-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/34af3908-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/37cdab60-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/3aea9948-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/3dfcdb78-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/411b4f88-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/443b2dd2-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/475fc2b6-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/485e5730-9374-11eb-8891-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/4a8618dc-9e81-11eb-b942-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/5790a0f8-92b3-11eb-8891-3448edf59a40.jpg',
        'http://192.168.21.150/media/alarm/20210401132004987697/bc04bcac-9e81-11eb-b942-3448edf59a40.jpg',
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
                        "alarmLevel": random.randint(1, 2),
                        "areaNum": random.randint(0, 100)
                    },
                    "densityImage": random.choices(image_li)[0],
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
        topic = 'zvams/analysis/density/alarm'
        print(content)
        ret = publish.single(topic, json.dumps(content), qos=1, hostname=hostname, port=port,
            auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        import time
        publish_mq_message(get_data(time.time()))
        time.sleep(sep)
        # break
