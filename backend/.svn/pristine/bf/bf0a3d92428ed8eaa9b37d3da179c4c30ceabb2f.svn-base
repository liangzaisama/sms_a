import time
import random
from paho.mqtt import publish


def test(hostname='127.0.0.1', sep=30, port=1883):
    dev_li = [
        'FA5720B0-BEFA-4CFB-BEC0-1EAF3605D513',
        'F8590E6B-D673-4F5D-869F-648277867B24',
        'F6B50CF2-D2A4-4B1E-A5A9-F2D176A99914',
        'F3343149-232B-42CF-88D1-21CC5AFFE3AB',
        'F2A9535A-9D02-49BB-8D97-2C999EB4BE21',
        '6145EB85-FEFB-4F22-BF53-9B006196873F',
        '573F72D2-D96D-4BBB-AE1D-3CF411BF07F1',
        '608E5DCE-5A3B-4534-A284-D431644D1E32',
        '6A9683CF-3293-481B-B994-3B41CB1D52A7',
        '6AE395B9-A27B-4FF8-B768-31F3063CBEF9',

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
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
            },
            "body":{
                "device": {
                "device_code": random.choices(dev_li)[0],
                "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                "ip": "192.168.21.185", "port": 554,
                "areaName": "1"
                },
                "passenger":{
                    'time': time.time(),
                    'analyzerResult':{
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
        topic = 'zvams/analysis/people/queue'
        publish.single(topic, json.dumps(content), qos=1, hostname=hostname, port=port,
            auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        import time
        publish_mq_message(get_data())
        time.sleep(sep)
        # break
