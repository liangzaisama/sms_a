from paho.mqtt import publish
import uuid


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
                  "device_code":'设备新增测试:2',
                  "device_name":'名称修改测试',
                  "ip":"192.168.110.123",
                  "device_type_id":"123123",
                  "device_type_id_son":"1",
                  "device_type_name":"Camera",
                  "area_code":"C7-1",
                  "floor_code":"B11",
                  "port": "1883",
                  "switches": "123123",
                  "related_camera_code1": "812732873",
                  "device_location":"航站楼2号",
                  "device_cad_code":"航站楼2号航站楼2号航站楼2号航站楼2号",
                  "manufacturer_code":"001",
                  "device_model":"1.0",
                  'device_state': 'normal',
                  'error_code': 'trouble_open',
                  'error_message': 'trouble_open',
                  "ptz":"Yes",
                  "rtsp":"rtsp://onvif:Labtest@123@192.168.100.202:554/live/293f919e-9993-4dbe-a943-17e0bd43bf36",
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
    topic = 'vms/device/update'
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


publish_mq_message(update)
