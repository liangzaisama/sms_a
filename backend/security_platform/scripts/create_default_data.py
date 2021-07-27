from itertools import islice
from collections import OrderedDict

import pandas as pd
from django.conf import settings


class CreateDefaultModelData:

    def __init__(self, app_name, model_name):
        self.app_name = app_name
        self.model_name = model_name

    def get_export_data(self, file_path=settings.API_SETTINGS.EXPORT_PATH, **kwargs):
        """读取excel数据"""
        data = pd.read_excel(file_path, self.model_name)
        for i in data.index:
            yield OrderedDict(data.loc[i], **kwargs)

    def bulk_create_data(self, model_class, batch_data):
        """批量创建模型类数据"""
        batch_size = 100
        objs = (model_class(**data) for data in batch_data)

        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break

            model_class.objects.bulk_create(batch, batch_size, ignore_conflicts=True)

    def single_create_data(self, model_class, batch_data):
        """依次创建"""
        for data in batch_data:
            try:
                model_class.objects.create(**data)
            except Exception as e:
                print(f'数据导入失败:{e}')
                print(f'导入设备数据:{data}')

    def single_sync_data(self, model_class, batch_data):
        """依次创建"""
        for data in batch_data:
            try:
                model_class.objects.update_or_create(
                    name=data['name'],
                    defaults=data
                )
            except Exception as e:
                print(f'数据导入失败:{e}')
                print(f'导入设备数据:{data}')

    def __call__(self, *args, **kwargs):
        """接收migrate信号时执行"""
        model_class = kwargs['apps'].get_model(self.app_name, self.model_name)

        if not model_class.objects.count():
            excel_batch_data = self.get_export_data()
            self.bulk_create_data(model_class, excel_batch_data)
