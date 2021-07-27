import time
import json
import random
from concurrent.futures.process import ProcessPoolExecutor

from paho.mqtt.client import Client


def worker(*args):
    client = Client(client_id='lwlwlwlwlwlwlwlwlwlllll')
    client.username_pw_set('admin', 'admin')
    client.connect_async('127.0.0.1', port=1884, keepalive=65535)
    client.loop_start()
    topic = 'zvams/analysis/density/alarm'

    dev_li = ['69D25210-AADA-4E22-A8FD-1CED20749475', '02FAB9A8-4165-4952-87E8-A9E2B45A65A8', ]

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
                "session_id":time.time(),
                "time_stamp":"20171208140658867"
            },
            "body":{
                "device": {
                    "device_code": '69D25210-AADA-4E22-A8FD-1CED20749475',
                    "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                    "ip": "192.168.21.185",
                    "port": 554,
                    "areaName": "1"
                },
                "passenger":{
                    "time": time.time(),
                    'analyzerResult': {
                        "alarmLevel": 1,
                        "areaNum": 1
                    },
                    "densityImage": 'http://192.168.21.150/media/alarm/20210401132004987697/31893c06-9e81-11eb-b942-3448edf59a40.jpg'
                }
            }
        }
        }

    while True:
        time.sleep(0.1)
        ret = client.publish(topic=topic, payload=json.dumps(get_data()), qos=1)


def main():
    max_workers = 1
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(worker, range(max_workers))

        while True:
            time.sleep(100)


if __name__ == '__main__':
    main()
