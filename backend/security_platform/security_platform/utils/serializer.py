"""
自定义序列化器
SerializerErrorHandle 许可化器错误处理，增加错误码映射
CustomSerializer Serializer基础上增加自定义异常抛出
CustomModelSerializer  ModelSerializer基础上增加批量更新，自定义异常抛出
"""
from collections import OrderedDict
from collections.abc import Mapping

from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from rest_framework.fields import SkipField, set_value, get_error_detail, ListField
from django.core.exceptions import ValidationError as DjangoValidationError

from security_platform import RET, ErrorType
from security_platform.utils.exceptions import MyExceptionError
from security_platform.utils.mixins import CustomErrorHandleMixin


class CustomCharField(serializers.CharField):
    """自定义字符串字段"""

    def get_attribute(self, instance):
        """获取对象的关联外键的属性

        如果关联外键不存在时，返回None, 不重写时会抛出AttributeError异常

        Args:
            instance: 模型数据对象

        Returns:
            获取对象关联的外键对象
        """
        try:
            return super().get_attribute(instance)
        except AttributeError:
            return None


# noinspection PyUnresolvedReferences,PyTypeChecker
class SerializerErrorHandle(CustomErrorHandleMixin):
    """
    序列化器错误处理
    """
    external_error_code = [
        ErrorType.MAX_LENGTH,
        ErrorType.MIN_LENGTH,
        ErrorType.MAX_VALUE,
        ErrorType.MIN_VALUE,
        ErrorType.INVALID_IMAGE,
        ErrorType.INVALID_EMAIL,
        ErrorType.INVALID_FORMAT,
        ErrorType.UNIQUE,
        ErrorType.MAX_COUNT
    ]

    def get_error_kwargs(self, error_code, field):
        """获取异常错误字符串格式化参数

        Args:
            error_code: 错误类型
            field: 异常错误序列化器字段对象

        Returns:
            error_kwargs: 错误格式化参数字典
        """
        error_kwargs = OrderedDict()
        error_kwargs['code'] = error_code

        if error_code in self.external_error_code:
            # 外部参数异常
            error_kwargs['errcode'] = RET.EXPARAMERR
            error_kwargs['param_name'] = field.label
        else:
            error_kwargs['param_name'] = field.label

        if error_code in ['max_length', 'min_length']:
            error_kwargs['max_length'] = getattr(field, "max_length", None) or 50
            error_kwargs['min_length'] = getattr(field, "min_length", None) or 1
        elif error_code in ['max_value', 'min_value']:
            error_kwargs['max_value'] = getattr(field, "max_value", None) or 50
            error_kwargs['min_value'] = getattr(field, "min_value", None) or 1
        elif error_code == ErrorType.DOES_NOT_EXIST:
            error_kwargs['model_name'] = field.label

        # TODO 其余错误类型字段待补全
        # elif ....

        return error_kwargs

    def errors_process(self, errors, field):
        """序列化器错误描述处理

        根据序列化器抛出的异常转为自定义异常
        根据错误类型进行错误码和错误描述映射

        Args:
            errors: 序列化器抛出的校验异常
            field: 校验异常的字段对象

        Raises:
            ParamError: 抛出自定义的参数异常
        """
        field_name = field.field_name
        exc = errors.get(field_name)

        if isinstance(exc, list):
            error_code = exc[0].code
            self.validate_error(**self.get_error_kwargs(error_code, field))

        elif isinstance(exc, dict):
            if isinstance(field, ListField):
                self.errors_process({field_name: exc.popitem()[1]}, field)

            # TODO 其余错误格式待补全

        self.validate_error(param_name=field_name)

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(datatype=type(data).__name__)
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]}, code=ErrorType.INVALID)

        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except MyExceptionError:
                # 自定义错误
                raise
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

            if errors:
                # print(errors)
                self.errors_process(errors, field)

        return ret


class CustomSerializer(SerializerErrorHandle, serializers.Serializer):
    """Serializer基础上增加自定义错误处理"""
    pass


class CustomModelSerializer(SerializerErrorHandle, serializers.ModelSerializer):
    """ModelSerializer基础上增加自定义错误处理"""

    def depth_limit_fields(self):
        """默认关联对象的限制字段"""
        return '__all__'

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """

        class NestedSerializer(serializers.ModelSerializer):
            """嵌套序列化器"""
            class Meta:
                """模型类配置

                fields：要查询的字段，如果有设置限制字段就使用，如果没有就返回全部字段
                """
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = getattr(self, f'{field_name}_depth_limit_fields', self.depth_limit_fields)()

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    @property
    def user(self):
        """用户对象"""
        assert 'request' in self.context, '序列化器缺少请求对象'
        return self.context['request'].user
