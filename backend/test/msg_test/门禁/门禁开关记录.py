from paho.mqtt import publish
import uuid

delete = {
	"msg": {
		"head": {
	            "service_code":"SMP_ACS_DEVICE_ADD",
                "version":'1.0',
                "sender_platform":"SMP",
                "sender_sys":"ACS",
                "receiver_platform":"",
                "receiver_sys":"",
                "session_number":"",
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
		    },
		"body": {
			  "device": {
                  "device_code": "d915aec8-2edd-11eb-b5a3-acde48001122",
			    }
		}
	}
}

data = {
	"msg": {
		"head": {
	            "service_code":"SMP_ACS_DEVICE_ADD",
                "version":'1.0',
                "sender_platform":"SMP",
                "sender_sys":"ACS",
                "receiver_platform":"",
                "receiver_sys":"",
                "session_number":"",
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
		    },
		"body": {
			  "device": {
                  "device_code":str(uuid.uuid1()),
                  "device_name":str(uuid.uuid4()),
                  "ip":"192.168.110.123",
                  "device_type_id":"123123",
                  "device_type_id_son":"dddfffff",
                  "device_type_name":"camera",
                  "area_code":"安检口1",
                  "port": "1883",
                  "switches": "123123",
                  "related_camera_code1": "812732873",
                  "device_location":"航站楼2号",
                  "device_cad_code":"001-J-101-101",
                  "manufacturer_code":"001",
                  "device_model":"1.0",
                  "ptz":"Yes",
                  "rtsp":"rtsp://onvif:Labtest@123@192.168.100.202:554/live/293f919e-9993-4dbe-a943-17e0bd43bf36",
			    }
		}
	}
}

status = {
	"msg": {
		"head": {
	            "service_code":"SMP_ACS_DEVICE_ADD",
                "version":'1.0',
                "sender_platform":"SMP",
                "sender_sys":"ACS",
                "receiver_platform":"",
                "receiver_sys":"",
                "session_number":"",
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
		    },
		"body": {
			  "entrance_door": {
                  "device_code":'B区_键盘读卡器_B23',
                  "open_or_close_time":'20210415140658867',
                  "door_status":0,
			    }
		}
	}
}

update = {
	"msg": {
		"head": {
	            "service_code":"SMP_ACS_DEVICE_ADD",
                "version":'1.0',
                "sender_platform":"SMP",
                "sender_sys":"ACS",
                "receiver_platform":"",
                "receiver_sys":"",
                "session_number":"",
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
		    },
		"body": {
			  "device": {
                  "device_code":'d915aec8-2edd-11eb-b5a3-acde48001122',
                  "device_name":str(uuid.uuid4()),
                  "ip":"192.168.110.123",
                  "device_type_id":"123123",
                  "device_type_id_son":"device_type_id_son",
                  "device_type_name":"camera",
                  "area_code":"C7-1",
                  "floor_code":"B11",
                  "port": "1883",
                  "switches": "123123",
                  "related_camera_code1": "812732873",
                  "device_location":"航站楼2号",
                  "device_cad_code":"航站楼2号航站楼2号航站楼2号航站楼2号",
                  "manufacturer_code":"001",
                  "device_model":"1.0",
                  "ptz":"Yes",
                  "rtsp":"rtsp://onvif:Labtest@123@192.168.100.202:554/live/293f919e-9993-4dbe-a943-17e0bd43bf36",
			    }
		}
	}
}

import time
# 门禁刷卡信息
slot = {
	"msg": {
		"head": {
	            "service_code":"SMP_ACS_DEVICE_ADD",
                "version":'1.0',
                "sender_platform":"SMP",
                "sender_sys":"ACS",
                "receiver_platform":"",
                "receiver_sys":"",
                "session_number":"",
                "session_id":"格式：UUID",
                "time_stamp":"20171208140658867"
		    },
		"body": {
			    "entrance_punch": {
                "entrance_punch_code":"000001_EntrancePunch_171221111432",
                "device_code":"000001_000103_171221111432",
                "record_time":"20171221111432",
                "card_no":"000001000103000001",
                "holder": time.time(),
                "department":"旅检一部",
                "in_out":"1",
                "region_id":"000001",
                "jobs":"安检员",
                "code_name":"000001"
            }
		}
	}
}


# camera = 'VMS', '视频监控系统'
# maintenance = 'AIS', '围界系统'
# entrance = 'ACS', '门禁系统'
# fire = 'XFHZ', '消防系统'
# conceal = 'YBBJ', '隐蔽报警系统'
# passage = 'CMS', '道口系统'


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    import json
    topic = 'acs/accesscontrol/door'
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


publish_mq_message(status)
