import time
from paho.mqtt import publish



data = {"msg": {"head": {
    "service_code": "SMP_VAMS_BEHAVIOR_ALARMINVASION",
    "version": "1.0", "sender_platform":
        "SMP", "send_sys": "VMS",
    "session_id": "7ca64f26-6907-11eb-ad95-4cd98f23cbcc",
    "time_stamp": "20210207134404189"},
    "body": {
        "device": {
            "device_code": '057b7481-66ec-415d-b10a-275cd07bd8f2',
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
                "time": 1612723476,
                "url": "http://192.168.21.150/media/alarm/20210207132250744399/86cc65ae-6974-11eb-8e4f-3448edf59a40.jpg",
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
    # topic = 'zvams/discern/behavior/posture'
    topic = 'zvams/discern/behavior/border'
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    time.sleep(1)
    data['msg']['head']['session_id'] = time.time()
    print(data)
    publish_mq_message(data)
    break
