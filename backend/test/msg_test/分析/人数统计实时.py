import random, time
from paho.mqtt import publish


def test(hostname='127.0.0.1', sep=30, port=1883):
    print('人数统计', hostname)
    dev_li = [
        '6920718D-599D-4C54-8589-4FFDF8E08814',
        '6145EB85-FEFB-4F22-BF53-9B006196873F',
        '573F72D2-D96D-4BBB-AE1D-3CF411BF07F1',
        'EC5F8848-D715-4887-AEA9-FDB0B0EA5B82',
        'E9972B4C-2EB2-46E3-AEE4-9D62AAF3C48F',
        '9261CB9F-F83D-49D4-8DCD-FC135BE310A9',
        '2A44B535-3202-4451-8D3E-D53E5E021B0D'
        # 'f6d2e2f7-2d83-4b0d-9036-4e67b3cc5bfb',
        # 'E026F4E4-2812-41E0-A49D-3438FD897363',
        # '477D2CC1-CDCD-48AC-8596-2806FEEBC834',
    ]

    ti = ['05BCDA17-BB29-4D92-A60E-4B3AD6AC746A']

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
                "device_code": random.choices(ti)[0],
                "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                "ip": "192.168.21.185",
                "port": 554,
                "areaName": "1"
            },
                "passenger":{
                    'result':{
                        'time': time.time(),
                        'data':{
                            'upgoing': 1,
                            "areaNum": random.randint(0, 100)
                        }
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
        publish.single(topic, json.dumps(content), qos=1, hostname=hostname, port=port,
            auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        publish_mq_message(get_data())
        time.sleep(sep)
        # break


if __name__ == '__main__':
    test()