import random, time
from paho.mqtt import publish


def test(hostname='192.168.21.97', sep=30, port=1883):
    dev_li = [
        # '设备新增测试:11381',
        '6920718D-599D-4C54-8589-4FFDF8E08814',
        '6145EB85-FEFB-4F22-BF53-9B006196873F',
        'EB403AE2-4772-49D6-9B94-B2AF5C474FDD',
        '9261CB9F-F83D-49D4-8DCD-FC135BE310A9'
    ]

    image_li = [
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_01_18_1384.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_01_18_2188.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_10_17_2975.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_10_17_9568.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_32_08_4101.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_32_08_8189.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_45_47_4688.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_45_48_5047.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_45_49_3510.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/09_45_49_6061.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/10_54_50_1617.jpg',
        'http://192.168.21.150/media/faceCap/20210225/192.168.21.186/10_54_50_2667.jpg',
    ]
    import time

    def get_data():
        return {
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
                                    "device_code": random.choices(dev_li)[0],
                                    # "device_code": '77BB0718-9230-494A-956E-F1080C327542',
                                    "device_name": "UNIVIEW IPC-E242-IR@DUACP-IR5-DH (192.168.21.185)",
                                    "ip": "192.168.21.185",
                                    "port": 554,
                                    "areaName": "1"
                                },
                            "person_monitor": {
                                "action": "0",
                                "width": 432,
                                "height": 420,
                                "imgUrl": random.choices(image_li)[0],
                                "time": time.time(),
                                "qualityScore": 0.9995185136795044,
                                "feature": "AAAAgHE/jL8AAAAg+Ne7PwAAAIC6YIw/AAAAAFIsf78AAACAy2OgvwAAAGDinqm/AAAAQOTvob8AAABgP/i8vwAAAIAxh8A/AAAAAMcOr78AAADg82DKPwAAAIAPxKa/AAAAQBBpx78AAAAgNYm6vwAAAADK8Hi/AAAAgE7Qxz8AAAAAxffFvwAAAGARarq/AAAAwG0Ytr8AAACAKGqZvwAAAABtDKg/AAAAQKtRoD8AAACAb9qtPwAAAIC3bIG/AAAAQN7Op78AAACAJC7WvwAAAGCAgbO/AAAAAA5yt78AAAAA38GdPwAAAADaDla/AAAA4APitL8AAACg3ki0PwAAACAhqMC/AAAAIGE7wb8AAABAQo+7PwAAAOBOKcA/AAAAgFDRor8AAABARUGqvwAAAIAAjs4/AAAAAFT0Tz8AAABAMi7GvwAAAIAL/ak/AAAAAEiZtD8AAACA2i3RPwAAAADt984/AAAAYC1Aqj8AAAAgxj2jPwAAAGAPmMG/AAAAQIpvwD8AAAAgQn3BvwAAAIAjzaI/AAAAQKQ/wj8AAADAFtK5PwAAAOBF+7w/AAAAQD4Hib8AAAAAhwe7vwAAAAAYuLs/AAAAwAWVsj8AAADAKMfCvwAAAMBoJ6O/AAAAQK+cwj8AAACg4ivAvwAAAGAVapW/AAAAoDFZgT8AAABgoyDRPwAAAED/05g/AAAAALF9ub8AAADgr1nHvwAAAGCOQbM/AAAAQIqRwL8AAADAQlC/vwAAAAAvHY+/AAAAYMm3yL8AAAAAI+m3vwAAAADfidW/AAAAwFyvfz8AAABgslXZPwAAAMCcPqs/AAAAwLcUxr8AAAAAoMG4PwAAAGCNbKm/AAAAANRxlr8AAADAvcDCPwAAACAcPsY/AAAAgM/Xpb8AAAAApwN4vwAAACCUE7e/AAAAAOcXhb8AAACATHXLPwAAAIAAdbG/AAAAgJV5sb8AAACgLwrEPwAAAEA17ZS/AAAAoGvzvD8AAACgeOWuPwAAAECYd5g/AAAAYNWNqr8AAADANt6tPwAAAABJc8C/AAAAAIwMkr8AAADg44u4PwAAAAB6FrG/AAAAwLWSmz8AAADgCH3CPwAAAKAlfMm/AAAAYPq9vj8AAAAAvQKpvwAAAABwk7c/AAAAINS8uT8AAADA6E2kvwAAAEAM/rS/AAAAQOWRrr8AAAAg+krDPwAAAEA81ce/AAAAAJpayT8AAAAgw0DIPwAAAADmQ6U/AAAAgCYcsz8AAAAAQAfDPwAAAMD+6rk/AAAAAFBncb8AAAAge4yrPwAAAKDW5dG/AAAAIGQUi78AAABg9VKxPwAAACCG2qU/AAAAQITeuT8AAACgdMOmPw==",
                                "eventSeq": 49,
                                "faceRect": [93.0, 60.46875, 301.875, 320.15625],
                                "similars": {
                                    "dbId": 29,
                                    "users": {
                                        "score": 0.8,
                                        "userIdx": "3b3796c4669311eb89cb4cd98f23cbcc",
                                        "dbImageUrl": random.choices(image_li)[0],
                                        "personInfo": {
                                            'sex': 0,
                                            'db_type': '1',
                                            'type': 1,
                                            'customType': '0',
                                            'db_name': '黑名单',
                                            'name': random.choices(['李安修', '王晓亚', '李飞', '宋子亮'])[0],
                                            'born': '1993-11-05',
                                            'number': '37808212313213123123',
                                            'city': '北京',
                                            'country': '中国',
                                            'monitor_type': 'alarm',
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
        topic = 'zvams/alarm/trigger'
        publish.single(topic, json.dumps(content), qos=1, hostname=hostname, port=port,
            auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')

    while True:
        import time
        publish_mq_message(get_data())
        time.sleep(sep)
        break
