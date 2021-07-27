import os
import sys
import requests
import time

import django
from django.db import transaction

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(BASE_DIR))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'security_platform.settings.dev'
    django.setup()

from security_platform import config_parser


def get_camera():
    response = requests.post(url=f"{config_parser.get('CAMERA', 'CAMERA_SERVER')}/vms/cameras", data={'username': 'admin', 'password': 'admin'})


def get_event_picture():
    pass


def request_zvams(url, token=None, post=True):
    """
    调用webapi
    """
    print(url)
    try:
        if post:
            response = requests.post(url=url, data={'username': 'admin', 'password': 'admin'})
        else:
            response = requests.get(url=url, headers={'Authorization': token})

        print(response.status_code)
        response_data = response.json()
    except Exception as e:
        print('获取数据失败: %s' % e)
        return

    # print(response_data)
    if response_data.get('result') == 'error':
        print('获取数据失败: %s' % response_data['errorMessage'])
        return

    return response_data


def get_data():
    """
    导入摄像头数据
    """
    # 获取token
    from devices.models import CameraDevice

    response_data = request_zvams(f"{config_parser.get('API_HOST', 'ZVAMS')}/userlogin")
    token = response_data['accessToken']

    # 获取实体类型
    response_data = request_zvams(f"{config_parser.get('API_HOST', 'VMS')}/vms/entityTypes", token, post=False)

    # 获取摄像头 /vms/CameraDevices
    # response_data = request_zvams(f"{config_parser.get('API_HOST', 'VMS')}/vms/cameras?isVideoAnalysis=true", token, post=False)
    response_data = request_zvams(f"{config_parser.get('API_HOST', 'VMS')}/vms/CameraDevices/", token, post=False)

    for i in response_data['data']:
        if i['ip'] == '172.37.124.151':
            print(i)

    # for video in response_data['data']:
    #     try:
    #         camera = CameraDevice.objects.create(
    #             device_name=video['entityName'],
    #             device_code=video['entityId'],
    #             device_type_id=video['entityTypeId'],
    #             device_type_name=video['entityTypeName'],
    #             device_type='cctv',
    #             belong_system='VMS',
    #             flow_address=video['Propertys']['rtsp'],
    #             is_ptz=True if video['Propertys']['PTZ'] == 'YES' else False
    #         )
    #     except Exception as e:
    #         print(e)


if __name__ == '__main__':
    get_data()
