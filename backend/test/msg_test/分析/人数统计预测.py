import time
import random
from paho.mqtt import publish
dev_li = [
    '057b7481-66ec-415d-b10a-275cd07bd8f2',
    'f6d2e2f7-2d83-4b0d-9036-4e67b3cc5bfb',
    # '477D2CC1-CDCD-48AC-8596-2806FEEBC834',
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
        "body":{"device": {
            "device_code": random.choices(dev_li)[0],
            "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)", "ip": "192.168.21.185", "port": 554,
            "areaName": "1"
        },
            "passenger":{
                'time': time.time() - (86400 * random.randint(1, 4) * 7),
                # 'time': '1614957137.463206',
                'analyzerResult':{
                    'upGoing': 1,
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
    topic = 'zvams/analysis/people/counting'
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    time.sleep(1)
    publish_mq_message(get_data())
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