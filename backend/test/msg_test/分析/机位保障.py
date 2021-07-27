import random
import time

from paho.mqtt import publish


def safe():
    import time
    dev_li = [
        '77BB0718-9230-494A-956E-F1080C327542',
        # 'C182B69B-7D5E-490B-8D5C-AB41A7E69BE6',
        # 'B75A66EF-4B2B-4AE6-A01D-0B2512EB6C5B'
    ]

    def get_data():
        return {
            "msg":
                {
                    "head":
                         {
                             "service_code": "SMP_VAMS_BEHAVIOR_ALARMWANDERING",
                             "version": "1.0",
                             "sender_platform": "SMP",
                             "send_sys": "VMS",
                             "session_id": time.time(),
                             "time_stamp": time.time()
                         },
                        "body": {
                            "device":
                                {
                                    "device_code": random.choices(dev_li)[0],
                                    "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                                    "ip": "192.168.21.185",
                                    "port": 554,
                                    "areaName": "1"
                                },
                            "apron": {
                                'taskId': 2021032313123,
                                'operation': 'video',
                                'result': {
                                    'time': time.time(),
                                    "url": 'http://192.168.21.150/media/backend_dev/plane.jpeg',
                                    # 'state': random.choices([0,1,2,3,4,5,6,7,10,11,12,13,14,15,16,17,18,19,20])[0],
                                    'state': 10,
                                }
                            }
                        }
                    },
            "tag": 139
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
        topic = 'zvams/discern/object/apron'
        publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
                       auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        publish_mq_message(get_data())
        time.sleep(10)
        # break


safe()
