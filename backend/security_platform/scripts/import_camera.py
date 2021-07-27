"""
摄像机导入脚本
"""
import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'mqtt_receive'))

try:
    from manage import set_django_module
    set_django_module()
    django.setup()

    from mqtt_receive.core.generics import LabelResourceBulkProxy
    from mqtt_receive.views.device import CameraDeviceResource
    from devices.apps import create_gis_point
    from devices.models import CameraDevice
    from devices.utils import request_vms, RequestVMSError
    from configurations.models import GisPoint
except ImportError:
    raise ImportError("Couldn't import DJANGO_SETTINGS_MODULE")


if __name__ == '__main__':
    try:
        create_gis_point(GisPoint)
        camera_list = request_vms('vms/CameraDevices', 'get')
    except RequestVMSError as e:
        print(e)
    else:
        LabelResourceBulkProxy(camera_list, (), CameraDeviceResource, disable_ws=True).synchronization()
