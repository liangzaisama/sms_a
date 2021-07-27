import time
from paho.mqtt import publish


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
            "event":{
                "event_name":"徘徊123",
                "event_code": time.time(),
                "device_code":"4D3D10EB-2EAB-4D6B-B03E-713B28C2B71B",
                "event_time":"20171221111432",
                "event_type":"00001",
                "event_message":"门/磁错开",
                "area_code":"C5-8",
                "priority":"4",
                "floor_code": "B1",
                "passcard_id": "2187361723678",
                "picture_paths":[
                     "FTP://CMS.com/CMS1.jpg",
                     "FTP://CMS.com/CMS2.jpg ",
                     "FTP://CMS.com/CMS3.jpg "
                ],
                "camer_list":[
                {
                    "camer_guid":"000001_000103_171221111432_123456_54321",
                    "camer_persetid":None
                },
                {
                    "camer_guid":"000001_000103_171221111432_123456_8888",
                    "camer_persetid":"1"
                }
                ]
            }
        }
    }
    }

f = {"msg":{"head":{"service_code":"SMP_VMS_ALARM_TRIGGER","version":"1.0","sender_platform":"SMP","sender_sys":"VMS","receiver_sys":"","session_id":"6f47838f-7847-42ba-8bb1-fa376eaff393","time_stamp":"20210421135831727"},"body":{"event":{"event_name":"密度报警","event_code":"74c55f66-a266-11eb-b835-70b5e8d1f7b1a","device_code":"2706362b-2fc5-49fe-96ff-907aafe958a3","event_time":"20210421135727000","event_type":"0","event_message":"密度报警","area_code":None,"priority":"3","camer_list":[]}}}}


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    import json
    topic = 'ais/alarm/trigger'
    publish.single(topic, json.dumps(content), qos=1, hostname='10.129.137.33',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


# for i in range(1000):
publish_mq_message(f)
