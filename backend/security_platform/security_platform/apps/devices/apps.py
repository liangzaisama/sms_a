import os
import sys
from collections import OrderedDict
from itertools import islice

import pandas as pd
from django.conf import settings
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from devices.utils import request_vms, RequestVMSError


def get_export_data(sheet_name, file_path=settings.API_SETTINGS.EXPORT_PATH, **kwargs):
    """读取excel数据"""
    data = pd.read_excel(file_path, sheet_name)
    for i in data.index:
        yield OrderedDict(data.loc[i], **kwargs)


def bulk_create_data(model_class, batch_data):
    """批量创建"""
    batch_size = 100
    objs = (model_class(**data) for data in batch_data)

    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break

        model_class.objects.bulk_create(batch, batch_size, ignore_conflicts=True)


def single_create_data(model_class, batch_data):
    """依次创建"""
    for data in batch_data:
        try:
            model_class.objects.create(**data)
        except Exception as e:
            print(f'数据导入失败:{e}')
            print(f'导入设备数据:{data}')


# def get_vms_access_token():
#     """获取vms接口凭证"""
#     try:
#         response = requests.post(
#             f"{config_parser.get('API_HOST', 'ZVAMS')}/userlogin",
#             data={'username': 'admin', 'password': 'admin'}
#         )
#
#         return response.json()['accessToken']
#     except Exception as e:
#         print('获取token失败:', e)
#
#
# def get_vms_camera_list(token):
#     """获取vms接口凭证"""
#     try:
#         response = requests.get(
#             f"{config_parser.get('API_HOST', 'VMS')}/vms/CameraDevices",
#             headers={'Authorization': token}
#         )
#
#         print(response)
#         print(response.json()['result'])
#         return response.json()['data']
#     except Exception as e:
#         print('获取摄像机列表失败:', e)


def create_gis_point(GisPoint):
    # 导入gis点位信息
    gis_points = request_vms('vms/GisMapPoint', 'get')
    for gis_point in gis_points:
        defaults = OrderedDict()
        defaults['system_code'] = gis_point['SystemCode']
        defaults['object_id'] = gis_point['ObjectID']
        defaults['dev_guid'] = gis_point['DevGuid']
        defaults['map_id'] = gis_point['MapID']
        defaults['layer_id'] = gis_point['LayerID']
        defaults['floor_id'] = gis_point['FloorID']
        defaults['dev_name'] = gis_point['DevName']
        defaults['cad_name'] = gis_point['CadName']
        defaults['remark'] = gis_point['Remark']
        defaults['dev_type'] = gis_point['DevType']
        defaults['dev_manu'] = gis_point['DevManu']
        defaults['camera_ip'] = gis_point['CameraIP']
        defaults['x'] = gis_point['X']
        defaults['y'] = gis_point['Y']
        defaults['date_time'] = gis_point['DateTime']

        GisPoint.objects.update_or_create(
            dev_guid=gis_point['DevGuid'],
            defaults=defaults
        )


def create_default_camera_data(**kwargs):
    """创建默认摄像机数据"""
    sys.path.insert(0, os.path.join(os.path.dirname(settings.BASE_DIR), 'mqtt_receive'))

    from mqtt_receive.core.generics import LabelResourceBulkProxy
    from mqtt_receive.views.device import CameraDeviceResource

    try:
        GisPoint = kwargs['apps'].get_model('configurations', 'GisPoint')
        CameraDevice = kwargs['apps'].get_model('devices', 'CameraDevice')
    except LookupError as e:
        print(e)
        return

    if not GisPoint.objects.count():
        create_gis_point(GisPoint)

    if not CameraDevice.objects.count():
        # 导入摄像机信息
        try:
            camera_list = request_vms('vms/CameraDevices', 'get')
        except RequestVMSError as e:
            print(e)
        else:
            LabelResourceBulkProxy(camera_list, (), CameraDeviceResource, disable_ws=True).synchronization()


def create_default_test_camera_data(**kwargs):
    """创建北京测试摄像机数据"""
    try:
        CameraDevice = kwargs['apps'].get_model('devices', 'CameraDevice')
    except LookupError:
        return

    if not CameraDevice.objects.count():
        # 无数据，需要导入
        batch_data = list(get_export_data('camera', **{'belong_system': 'VMS', 'device_type': 'cctv'}))
        single_create_data(CameraDevice, batch_data)


def create_default_maintenance_data(**kwargs):
    """创建默认围界设备数据"""
    try:
        MaintenanceDevice = kwargs['apps'].get_model('devices', 'MaintenanceDevice')
        DeviceInfo = kwargs['apps'].get_model('devices', 'DeviceInfo')
        ResourceInfo = kwargs['apps'].get_model('situations', 'ResourceInfo')
    except LookupError:
        return

    if not MaintenanceDevice.objects.count():
        # 无数据，需要导入
        batch_data = list(get_export_data('maintenance', **{'belong_system': 'AIS', 'device_type': 'enclosure'}))

        for data in batch_data:
            if not pd.isnull(data['parent']):
                data['parent'] = DeviceInfo.objects.get(device_code=data['parent'])
            else:
                data.pop('parent')

            if pd.isnull(data['related_camera_code']):
                data.pop('related_camera_code')

            if data['area_code']:
                try:
                    res = ResourceInfo.objects.get(name=f'{data["area_code"].split("-")[0]}防区')
                except ResourceInfo.DoesNotExist:
                    # 没找到对应防区
                    print('防区未找到', data['area_code'])
                else:
                    data['resource'] = res

            try:
                MaintenanceDevice.objects.create(**data)
            except Exception as e:
                print(f'数据导入失败:{e}')
                print(f'导入设备数据:{data}')


def create_default_entrance_data(**kwargs):
    """创建默认门禁设备"""
    try:
        EntranceDevice = kwargs['apps'].get_model('devices', 'EntranceDevice')
    except LookupError:
        return

    if not EntranceDevice.objects.count():
        # 无数据，需要导入
        batch_data = list(get_export_data('entrance', **{'belong_system': 'ACS', 'device_type': 'access_control'}))
        single_create_data(EntranceDevice, batch_data)


def create_default_fire_data(**kwargs):
    """创建默认消防设备数据"""
    try:
        FireDevice = kwargs['apps'].get_model('devices', 'FireDevice')
    except LookupError:
        return

    if not FireDevice.objects.count():
        # 无数据，需要导入
        batch_data = list(get_export_data('fire', **{'belong_system': 'XFHZ', 'device_type': 'fire'}))
        single_create_data(FireDevice, batch_data)


def create_default_conceal_data(**kwargs):
    """创建默认隐蔽报警设备数据"""
    try:
        ConcealAlarmDevice = kwargs['apps'].get_model('devices', 'ConcealAlarmDevice')
    except LookupError:
        return

    if not ConcealAlarmDevice.objects.count():
        # 无数据，需要导入
        batch_data = list(get_export_data('conceal_alarm', **{'belong_system': 'YBBJ', 'device_type': 'alarm'}))
        single_create_data(ConcealAlarmDevice, batch_data)


def create_default_passage_way_data(**kwargs):
    """创建默认道口设备数据"""
    try:
        PassageWayDevice = kwargs['apps'].get_model('devices', 'PassageWayDevice')
        ResourceInfo = kwargs['apps'].get_model('situations', 'ResourceInfo')
    except LookupError:
        return

    if not PassageWayDevice.objects.count():
        # 无数据，需要导入
        extra_data = OrderedDict()
        extra_data['belong_system'] = 'CMS'
        extra_data['device_type'] = 'passage_way'
        try:
            res = ResourceInfo.objects.get(name='道口')
        except ResourceInfo.DoesNotExist:
            print('道口防区未找到')
        else:
            extra_data['resource'] = res

        batch_data = list(get_export_data('passage_way', **extra_data))
        single_create_data(PassageWayDevice, batch_data)


class DevicesConfig(AppConfig):
    name = 'devices'
    verbose_name = '设备管理'

    def ready(self):
        pass
        # post_migrate.connect(create_default_camera_data, sender=self)
        # # post_migrate.connect(create_default_test_camera_data, sender=self)
        # post_migrate.connect(create_default_maintenance_data, sender=self)
        # post_migrate.connect(create_default_entrance_data, sender=self)
        # post_migrate.connect(create_default_fire_data, sender=self)
        # post_migrate.connect(create_default_conceal_data, sender=self)
        # post_migrate.connect(create_default_passage_way_data, sender=self)
