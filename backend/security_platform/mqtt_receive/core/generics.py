"""MQ消息处理的工具类及函数

包含如下：
time_format_conversion: 时间格式转换的工具函数
GenericLabelResource: 数据标签数据库相关处理的工具类
"""
import os
import json
import datetime

from django.db.utils import IntegrityError
from django.db.models import ObjectDoesNotExist

from security_platform import config_parser, receive_logger as logger

from core.ws import ws_connections
from utils.exceptions import InvalidMsgFiledError, DuplicateError, WebsocketError


def time_format_conversion(date_string, format='%Y%m%d%H%M%S%f'):
    """时间格式转换

    '20171208140658867' 转成 datetime对象

    Args:
        date_string: 时间字符串
        format: 格式

    Returns:
        date_string: 转换后的datetime对象
    """
    if date_string is not None:
        return datetime.datetime.strptime(date_string, format)

    return date_string


def publish_ws_message(ws_suffix, message):
    """发送websocket消息

    发送websocket消息耗时 0.0002～0.0006, 耗时较短，无需做特殊处理
    """
    try:
        ws_connection = ws_connections[os.path.join(
            config_parser.get('WEBSOCKET', 'WEBSOCKET_ADDRESS'), ws_suffix
        )]

        message['publisher'] = True
        message['send_time'] = str(datetime.datetime.now())

        with ws_connection as conn:
            conn.send(json.dumps(message))
    except WebsocketError as exc:
        logger.error(exc)


def get_dict_nested_value(dict_instance, nested_keys):
    """消息数据标签解析"""
    for key in nested_keys:
        dict_instance = dict_instance[key]

    return dict_instance


# noinspection PyTypeChecker
class GenericLabelResource:
    """数据标签通用操作类

    通过获取标签数据及调用不同方法来实现对数据进行增删改等模型类的操作

    Class Attributes:
        model_class: 操作的模型类对象
        system_code: 消息所属系统编码

    Attributes:
        label: 传入的数据标签
    """

    model_class = None
    system_code = None

    def __init__(self, label, label_nested_seq=(), disable_ws=False):
        """标签初始化

        初始化中执行标签解析，标签对应模型内容创建

        Args:
            label: 原始数据标签
            label_nested_seq: 内容解析顺序
        """
        self.raw_label = label
        self.label = get_dict_nested_value(label, label_nested_seq)
        self.disable_ws = disable_ws  # 禁用websocket功能

    def reset_label(self, *args, **kwargs):
        """状态重新初始化, 用于同一对象处理多个标签数据"""
        self.__init__(*args, **kwargs)

    def get_model_class(self):
        """获取要操作的模型类对象

        Raises:
            AssertionError: 子类未定义model_class且未重写get_model_class
        """
        assert self.model_class is not None, (
            "'%s' should either include a `model_class` attribute, "
            "or override the `get_model_class()` method." % self.__class__.__name__
        )

        return self.model_class

    def get_system_code(self):
        """获取消息系统编号

        Raises:
            AssertionError: 子类未定义system_code且未重写get_system_code
        """
        assert self.system_code is not None, (
            "'%s' should either include a `system_code` attribute, "
            "or override the `get_system_code()` method." % self.__class__.__name__)
        return self.system_code

    def get_create_label(self):
        """获取新增标签数据"""
        raise NotImplementedError('method get_create_label() must be Implemented.')

    def get_update_label(self):
        """获取更新标签数据"""
        raise NotImplementedError('method get_update_label() must be Implemented.')

    def get_sync_label(self):
        """获取同步标签数据"""
        raise NotImplementedError('method get_sync_label() must be Implemented.')

    def get_object_label(self):
        """查找数据对象时的过滤条件"""
        raise NotImplementedError('method get_object_label() must be Implemented.')

    def get_object(self):
        """获取数据对象"""
        try:
            return self.get_model_class().objects.get(**self.get_object_label())
        except ObjectDoesNotExist as e:
            raise InvalidMsgFiledError(f'数据对象不存在:{e}')

    def validate_enum_filed(self, field_name, choices, integer=True, exception_default=None):
        """枚举字段校验"""
        try:
            value = self.label[field_name] if not integer else int(self.label[field_name])
            assert value in choices
        except (KeyError, AssertionError, TypeError, ValueError):
            if exception_default is None:
                raise InvalidMsgFiledError(f'{field_name}错误')

            self.label[field_name] = exception_default

    def publish_obj_ws_message(self, *objs):
        """推送ws消息"""
        if not self.disable_ws:
            for obj in objs:
                if hasattr(obj, 'ws_message') and hasattr(obj, 'WS_URL_SUFFIX'):
                    publish_ws_message(obj.WS_URL_SUFFIX, obj.ws_message)


class SwiftGenericLabelResource(GenericLabelResource):
    """新增/修改/同步数据统一处理资源对象"""

    def get_create_or_update_label(self):
        """新增/修改/同步数据统一处理"""
        raise NotImplementedError('method get_create_or_update_label() must be Implemented.')

    def get_create_label(self):
        return self.get_create_or_update_label()

    def get_update_label(self):
        return self.get_create_or_update_label()

    def get_sync_label(self):
        return self.get_create_or_update_label()


# noinspection PyUnresolvedReferences
class CreateModelMixin:
    """创建模型接口"""

    def create(self):
        """新增数据

        Returns:
            instance: 返回创建后的模型类对象
        """
        try:
            return self.get_model_class().objects.create(**self.get_create_label())
        except IntegrityError as e:
            if 'Duplicate entry' in str(e):
                raise DuplicateError(str(e))

            raise e


# noinspection PyUnresolvedReferences
class DeleteModelMixin:
    """删除模型接口"""

    def perform_destroy(self, instance, fake):
        if fake:
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted'])
            return instance

        return instance.delete()

    def delete(self, fake=False):
        """删除数据"""
        instance = self.get_object()
        return self.perform_destroy(instance, fake)


# noinspection PyUnresolvedReferences
class UpdateModelMixin:
    """更新模型接口"""

    def perform_update(self, instance, update_data):
        for attr, value in update_data.items():
            setattr(instance, attr, value)

        instance.save(update_fields=list(update_data.keys()))
        return instance

    def get_update_data(self, label_method):
        if label_method is not None:
            handler = getattr(self, label_method, None)
            assert handler is not None, (
                f"'{self.__class__.__name__}' should Implemented `{label_method}()` method."
            )

            update_data = handler()
        else:
            update_data = self.get_update_label()

        return update_data

    def update(self, label_method=None):
        """修改数据信息"""
        instance = self.get_object()
        return self.perform_update(instance, self.get_update_data(label_method))


# noinspection PyUnresolvedReferences
class SyncModelMixin:
    """同步模型接口"""

    def synchronization(self):
        """数据整表同步"""
        return self.get_model_class().objects.update_or_create(
            **self.get_object_label(),
            defaults=self.get_sync_label()
        )


class SwiftCommonLabelResource(SwiftGenericLabelResource,
                               CreateModelMixin,
                               DeleteModelMixin,
                               UpdateModelMixin,
                               SyncModelMixin):
    """数据标签增/删/更新/整表同步"""
    pass


class CreateUpdateLabelResource(GenericLabelResource,
                                CreateModelMixin,
                                UpdateModelMixin):
    """数据标签增/更新/"""
    pass


class CreateLabelResource(GenericLabelResource, CreateModelMixin):
    """数据标签增加"""
    pass


class SyncLabelResource(GenericLabelResource, SyncModelMixin):
    """数据标签同步或更新"""
    pass


class LabelResourceBulkProxy:
    """数据标签增/删/更新/整表同步"""

    def __init__(self, label, label_nested_seq, label_class, *args, **kwargs):
        self.raw_label = label
        self.labels = get_dict_nested_value(label, label_nested_seq)
        self.label_class = label_class
        self.label_class_args = args
        self.label_class_kwargs = kwargs
        self._label_class_obj = None
        self._context = kwargs.pop('context', {})  # 上下文信息

    def function_not_allowed(self, *args, **kwargs):
        raise NotImplementedError(f'{self.label_class.__class__.__name__} lack method.')

    def run_method_handler(self, function, *args, **kwargs):
        method_handler = getattr(self._label_class_obj, function, self.function_not_allowed)

        try:
            method_handler(*args, **kwargs)
        except Exception as e:
            logger.warning(f'批量消息处理失败:{e}', exc_info=True)

    def set_label_obj(self, label):
        if self._label_class_obj is None:
            self._label_class_obj = self.label_class(label, *self.label_class_args, **self.label_class_kwargs)
        else:
            self._label_class_obj.reset_label(label, *self.label_class_args, **self.label_class_kwargs)

    def _execute_label_class_func(self, function, *args, **kwargs):
        if isinstance(self.labels, dict):
            self.labels = [self.labels]

        for label in self.labels:
            label.update(self._context)

            self.set_label_obj(label)
            self.run_method_handler(function, *args, **kwargs)

    def create(self, *args, **kwargs):
        self._execute_label_class_func('create', *args, **kwargs)

    def delete(self, *args, **kwargs):
        self._execute_label_class_func('delete', *args, **kwargs)

    def update(self, *args, **kwargs):
        self._execute_label_class_func('update', *args, **kwargs)

    def synchronization(self, *args, **kwargs):
        self._execute_label_class_func('synchronization', *args, **kwargs)
