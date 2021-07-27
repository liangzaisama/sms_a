import os
import random
import time
import sys

import numpy
import django
from django.conf import settings

file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(file_path)
sys.path.insert(0, os.path.join(os.path.dirname(base_dir)))

from manage import set_django_module

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    set_django_module(environment='dev')
    django.setup()

import logging
logger = logging.getLogger('receive')


def t1():
    from django_redis import get_redis_connection
    while True:
        try:
            redis_conn1 = get_redis_connection('default')
            redis_conn2 = get_redis_connection('session')
            redis_conn3 = get_redis_connection('cache')
            print(redis_conn1, redis_conn2, redis_conn3)
            print(redis_conn1.get('lwl'))
            print(redis_conn2.get('lwl'))
            print(redis_conn3.get('lwl'))
            print('=='*100)
            time.sleep(2)
        except Exception as e:
            print(e)


def get_export_data(file_path=settings.API_SETTINGS.EXPORT_PATH, **kwargs):
    """读取excel数据"""
    import pandas as pd
    import numpy
    data = pd.read_excel(file_path, 'areas')
    area_dict = {}
    for i in data.index:
        ret = (dict(data.loc[i]))
        area_dict[ret['编号']] = ret['短名称']
    print(area_dict)
    camera_data = pd.read_excel(file_path, 'camera')
    for i in camera_data.index:
        area_code = camera_data.loc[i].area_code
        if isinstance(area_code, (numpy.int64, int)):
            # print(area_code)
            camera_data.loc[camera_data.area_code == area_code, 'area_code'] = area_dict[area_code]


def log_test():
    x = 0
    while True:
        x += 1
        logger.info('日志写入测试:%s', x)
        time.sleep(0.0001)


if __name__ == '__main__':
    t1()
