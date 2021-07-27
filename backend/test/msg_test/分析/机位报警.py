import time
from paho.mqtt import publish



data = {
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
                            "device_code": "1A19CA41-B6B7-4190-AFD4-0BD9D62EA1FD",
                            "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                            "ip": "192.168.21.185",
                            "port": 554,
                            "areaName": "1"
                        },
                    "placement": {
                        "action": "0",
                        "width": 432,
                        "height": 420,
                        "imgUrl": "http://192.168.21.150/media/faceCap/20210128/192.168.21.185/14_51_45_3245.jpg",
                        "time": 1611863505.0,
                        "qualityScore": 0.9995185136795044,
                        "feature": "AAAAgHE/jL8AAAAg+Ne7PwAAAIC6YIw/AAAAAFIsf78AAACAy2OgvwAAAGDinqm/AAAAQOTvob8AAABgP/i8vwAAAIAxh8A/AAAAAMcOr78AAADg82DKPwAAAIAPxKa/AAAAQBBpx78AAAAgNYm6vwAAAADK8Hi/AAAAgE7Qxz8AAAAAxffFvwAAAGARarq/AAAAwG0Ytr8AAACAKGqZvwAAAABtDKg/AAAAQKtRoD8AAACAb9qtPwAAAIC3bIG/AAAAQN7Op78AAACAJC7WvwAAAGCAgbO/AAAAAA5yt78AAAAA38GdPwAAAADaDla/AAAA4APitL8AAACg3ki0PwAAACAhqMC/AAAAIGE7wb8AAABAQo+7PwAAAOBOKcA/AAAAgFDRor8AAABARUGqvwAAAIAAjs4/AAAAAFT0Tz8AAABAMi7GvwAAAIAL/ak/AAAAAEiZtD8AAACA2i3RPwAAAADt984/AAAAYC1Aqj8AAAAgxj2jPwAAAGAPmMG/AAAAQIpvwD8AAAAgQn3BvwAAAIAjzaI/AAAAQKQ/wj8AAADAFtK5PwAAAOBF+7w/AAAAQD4Hib8AAAAAhwe7vwAAAAAYuLs/AAAAwAWVsj8AAADAKMfCvwAAAMBoJ6O/AAAAQK+cwj8AAACg4ivAvwAAAGAVapW/AAAAoDFZgT8AAABgoyDRPwAAAED/05g/AAAAALF9ub8AAADgr1nHvwAAAGCOQbM/AAAAQIqRwL8AAADAQlC/vwAAAAAvHY+/AAAAYMm3yL8AAAAAI+m3vwAAAADfidW/AAAAwFyvfz8AAABgslXZPwAAAMCcPqs/AAAAwLcUxr8AAAAAoMG4PwAAAGCNbKm/AAAAANRxlr8AAADAvcDCPwAAACAcPsY/AAAAgM/Xpb8AAAAApwN4vwAAACCUE7e/AAAAAOcXhb8AAACATHXLPwAAAIAAdbG/AAAAgJV5sb8AAACgLwrEPwAAAEA17ZS/AAAAoGvzvD8AAACgeOWuPwAAAECYd5g/AAAAYNWNqr8AAADANt6tPwAAAABJc8C/AAAAAIwMkr8AAADg44u4PwAAAAB6FrG/AAAAwLWSmz8AAADgCH3CPwAAAKAlfMm/AAAAYPq9vj8AAAAAvQKpvwAAAABwk7c/AAAAINS8uT8AAADA6E2kvwAAAEAM/rS/AAAAQOWRrr8AAAAg+krDPwAAAEA81ce/AAAAAJpayT8AAAAgw0DIPwAAAADmQ6U/AAAAgCYcsz8AAAAAQAfDPwAAAMD+6rk/AAAAAFBncb8AAAAge4yrPwAAAKDW5dG/AAAAIGQUi78AAABg9VKxPwAAACCG2qU/AAAAQITeuT8AAACgdMOmPw==",
                        "eventSeq": 49,
                        "faceRect": [93.0, 60.46875, 301.875, 320.15625],
                        "analyzerResult": {
                            "url": "http://192.168.21.150/media/backend/ceshi01_29/1611803247_8XtVpKSE.png",
                            "dbId": 29,
                            "users": {
                                "score": 0.6,
                                "userIdx": "3b3796c4669311eb89cb4cd98f23cbcc",
                                "dbImageUrl": "http://192.168.21.150/media/backend/ceshi01_29/1611803247_8XtVpKSE.png",
                                "personInfo": {
                                    'sex': 1,
                                    'name': '张三12',
                                    'born': '2020-11-05',
                                    'type': '身份证',
                                    'number': '37808212313213123123',
                                    'country': '中国',
                                    'city': '北京',
                                    'db_name': '黑名单',
                                    'monitor_type': 'alarm',
                                    'db_type': '黑名单',
                                    'customType': '0',
                                }
                            }
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
    topic = 'zvams/placement/alarm'
    publish.single(topic, json.dumps(content), qos=1, hostname='10.129.137.33',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


while True:
    import time
    time.sleep(5)
    data['msg']['head']['session_id'] = time.time()
    publish_mq_message(data)
