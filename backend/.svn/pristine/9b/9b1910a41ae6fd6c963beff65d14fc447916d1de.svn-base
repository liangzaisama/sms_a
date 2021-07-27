import datetime
import time
from paho.mqtt import publish


dev_li = [
    '62C2E028-2835-45ED-8CA7-875C3CE5A183',
    '662E74E1-9346-4D38-B8D4-23170AE86597',
    # 'E026F4E4-2812-41E0-A49D-3438FD897363',
    # '477D2CC1-CDCD-48AC-8596-2806FEEBC834',
]


data = {
            "msg":{
                "head":{
                    "service_code":"SMP_CMS_CAR_TRANSIT",
                    "version":"1.0",
                    "sender_platform":"SMP",
                    "sender_sys":"CMS",
                    "receiver_platform":"",
                    "receiver_sys":"",
                    "session_number":"",
                    "session_id":"29e6d489-0533-4b20-801c-f258b1ef7540",
                    "time_stamp":"2021042323060833"
                },
                "body":{
                    "car_transit": {
                        "device_code":"yl001",
                        "crossing_name":"yl001",
                        "car_direction":"1",
                        "record_time":"20210423230608",
                        "pass_status":"3",
                        "car_number":"G337Q",
                        "car_type":"保障",
                        "area_code":"飞行区",
                        "driver_card_number":"",
                        "driver_card_type":"",
                        "driver_name":"",
                        "driver_department":"",
                        "driver_telephonr ":"",
                        "picture_paths":["http://192.168.21.150/media/backend_dev/3.jpeg","",""]
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
    topic = 'cms/car/transit'
    publish.single(topic, json.dumps(content), qos=1, hostname=,
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    import random
    time.sleep(1)
    # data['msg']['head']['session_id'] = time.time()
    # data['msg']['body']['car_transit']['record_time'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    # data['msg']['body']['car_transit']['car_direction'] = random.randint(0, 1)
    publish_mq_message(data)
    # break
