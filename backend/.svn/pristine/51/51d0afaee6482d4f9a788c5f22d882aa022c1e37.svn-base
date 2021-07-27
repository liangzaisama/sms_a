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
                "device_code":"000001_000103_000001",
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
                    "camer_persetid":"1"
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


# print(data, type(data))
# import json
# ret = json.dumps(data)
# print(ret)
#
# print(data)

ack = {
    "msg":{
      "head":{
        "service_code":"RUC_AIS_ALARM_ACK",
        "version":"1.0",
        "sender_platform":"RUC",
        "sender_sys":"AIS",
        "receiver_platform":"SMP",
        "receiver_sys":"",
        "session_id":"格式：UUID",
        "time_stamp":"20171208140658867"
    },
    "body":{
        "event":
            {
            "event_code":"383b3c6e-e30a-4cde-bbad-3acf00db3a7f",
            "deactive_time":"20210301080341370",
            "deactive_message":"报警处置-误报",
       },
    }
}
}

ack = {
    "msg":{
            "head":{
                    "service_code":"SMP_VMS_ALARM_CHANGED",
                    "version":"1.0","sender_platform":
                    "SMP","sender_sys":"VMS","receiver_sys":"","session_id":"1f705f1f-a10a-47fc-b73a-63596079c15b",
                    "time_stamp":"20210301160340893"
            },
            "body":{
                "event":{
                    "event_code":"383b3c6e-e30a-4cde-bbad-3acf00db3a7f",
                    "deactive_time":"20210301080341370",
                    "deactive_user":"",
                    "deactive_message":"报警处置-误报"
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
    topic = 'vms/alarm/deactive'
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


for i in range(1):
    publish_mq_message(ack)

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