from paho.mqtt import publish
import random


def test(hostname='127.0.0.1', sep=30, port=1883):
    import time
    dev_li = [
        '9261CB9F-F83D-49D4-8DCD-FC135BE310A9',
        '2A44B535-3202-4451-8D3E-D53E5E021B0D'
        # 'E026F4E4-2812-41E0-A49D-3438FD897363',
        # '477D2CC1-CDCD-48AC-8596-2806FEEBC834',
    ]

    image_li = [
        'http://192.168.21.150/media/alarm/20200928113921281199/5161526c-013c-11eb-ba2a-4cd98f23cbcc.jpg',
        'http://192.168.21.150/media/alarm/20200928113921281199/71975c90-015d-11eb-99f2-4cd98f23cbcc.jpg',
        'http://192.168.21.150/media/alarm/20200928113921281199/7c3c13e8-0167-11eb-baf3-4cd98f23cbcc.jpg',
        'http://192.168.21.150/media/alarm/20200928113921281199/ce97d0b8-0154-11eb-80ef-4cd98f23cbcc.jpg',
    ]

    def get_data():
        return {
            "msg": {
                "head": {
                    "service_code": "SMP_VAMS_BEHAVIOR_ALARMINVASION",
                    "version": "1.0",
                    "sender_platform":"SMP",
                    "send_sys": "VMS",
                    "session_id": time.time(),
                    "time_stamp": "20210207134404189"
                },
                "body": {
                    "device": {
                        # "device_code": random.choices(dev_li)[0],
                        "device_code": 'B448815C-2CBD-465C-BD23-2DFC06EFDB3B',
                        "device_name": "HikVision DS-2CD3T25-I3 (192.168.20.233) - Camera 1",
                        "ip": "192.168.20.233",
                        "port": 554,
                        "areaName": "\\u5b89\\u68c0\\u5927\\u5385"
                    },
                    "behavior": {
                        'motionType': 1,
                        "taskId": "20210207132250744399",
                        "frameIdx": 7,
                        "frameDelay": 0.057569265365600586,
                        "operation": "video",
                        "resultType": 1,
                        "server_id": "ALG_4Ol0CvI1UVoq",
                        "msgType": 6,
                        "tag": 1612723476363395,
                        "msg_send_time": 1612723476.3634002,
                        "id": "7ca4d826-6907-11eb-ad95-4cd98f23cbcc",
                        "guid": "7ca4d826-6907-11eb-ad95-4cd98f23cbcc",
                        "cameraId": 12,
                        "cameraName": "HikVision DS-2CD3T25-I3 (192.168.20.233) - Camera 1",
                        "cameraVideoId": "4D3D10EB-2EAB-4D6B-B03E-713B28C2B71B",
                        "areaName": "",
                        "taskType": 9,
                        "seq": 36,
                        "analyzerResult": {
                            'motionType': 1,
                            "time": time.time(),
                            "url": random.choices(image_li)[0],
                            "width": 1920,
                            "height": 1080,
                            "rect": {"left": 734, "top": 0, "right": 867, "bottom": 378}}}}},
                            "tag": 91
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
        topic = 'zvams/discern/behavior/posture'
        publish.single(topic, json.dumps(content), qos=1, hostname=hostname, port=port,
            auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        import time
        publish_mq_message(get_data())
        time.sleep(sep)
        # break
