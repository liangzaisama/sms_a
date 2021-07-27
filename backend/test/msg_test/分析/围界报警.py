import time
import uuid
import random

from paho.mqtt import publish


def test(hostname='192.168.21.97', sep=30, port=1883):
    dev_li = [
        # '6044620F-E4E5-4B0F-9552-81D23B8EA698',
        # 'AD94CF6A-30F2-44C0-87C2-E8D2D553461A',
        # 'CE1CE885-770E-4595-80D6-C40A56DA8D01',

        '9B1147D3-B29F-4A82-A4E6-04236D97D381',
        '30a6d4e2-7212-4ff9-8d8a-4d062418251f',
        '2b1d4c92-8e65-4669-8daf-52fbfa0d7671',

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
                    "session_id":"01ae8d24-ac9e-4a46-a92e-60272461a1a1",
                    "time_stamp":"20210409163728"
                },
                "body":{
                    "event":{
                        "event_name":"围界报警",
                        "event_code":time.time(),
                        "device_code":"77BB0718-9230-494A-956E-F1080C327542",
                        "event_time":"20210409083717",
                        "event_type":"ManualAlarm",
                        "event_message":"围界报警",
                        "area_code":"C8-6防区",
                        "priority":"3",
                        "picture_paths":{
                            "addr1":"FTP://CMS.com/CMS1.jpg",
                            "addr2":"FTP://CMS.com/CMS3.jpg"
                        },
                        "camer_list":[
                            {"camer_guid":"ba686f34-b8c6-4569-8c01-0850634ba6a7","camer_persetid":""},
                            {"camer_guid":"993da74c-010e-431a-a6ed-bc813674704c","camer_persetid":""} ,
                            {"camer_guid":"fd5e5893-5ac7-4f78-af30-89ce29af9cba","camer_persetid":""},
                            {"camer_guid":"ae0a7b79-c004-4fff-bfbf-97ff5db2cd49","camer_persetid":""}
                        ]
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
        topic = 'vms/alarm/trigger'
        publish.single(topic, json.dumps(content), qos=1, hostname=hostname, port=port,
            auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        import time
        publish_mq_message(get_data())
        time.sleep(sep)
        break