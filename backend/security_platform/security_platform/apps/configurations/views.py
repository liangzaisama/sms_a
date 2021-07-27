from collections import OrderedDict

from django.db import transaction

from configurations.models import SystemConfig, GisMap
from configurations.serializers import ConfigSerializer, GisMapSerializer, GisLayerSerializer
from security_platform import ErrorType
from security_platform.utils.permisssions import DepartmentLeaderPermission
from security_platform.utils.views import CustomGenericAPIView


class GetVersionView(CustomGenericAPIView):
    """查询版本号

    需要跟rpm包的版本号一致
    """
    authentication_classes = ()
    permission_classes = ()
    versioning_class = None

    def get(self, _):
        """获取版本号"""
        # int('a')
        return self.success_response(data={'version': '2.2.15'})


class ConfigListUpdateView(DepartmentLeaderPermission, CustomGenericAPIView):
    """系统配置接口

    get:查询
    put:修改
    """
    serializer_class = ConfigSerializer

    def get(self, _):
        """获取配置列表"""
        data = OrderedDict()
        for config in SystemConfig.objects.all():
            if config.is_exposed:
                data[config.config_key] = config.value

        return self.success_response(data=data)

    def perform_update(self, serializer):
        """配置更新"""
        print(serializer.validated_data)
        with transaction.atomic():
            for config_key, config_value in serializer.validated_data.items():
                config = SystemConfig.objects.get(config_key=config_key)
                config.config_value = config_value
                config.save()

    def put(self, requests):
        """配置更新请求"""
        serializer = self.get_serializer(data=requests.data, partial=True)
        serializer.is_valid()
        self.perform_update(serializer)

        return self.success_response(data=serializer.validated_data)


class GisListView(CustomGenericAPIView):

    def get_map_instance(self, serializer):
        try:
            return GisMap.objects.get(**serializer.validated_data)
        except GisMap.DoesNotExist:
            self.validate_error(code=ErrorType.DOES_NOT_EXIST, model_name='gis地图')

    def get(self, request, *args, **kwargs):
        serializer = GisMapSerializer(data=request.query_params)
        serializer.is_valid()
        gis_map = self.get_map_instance(serializer)

        data = OrderedDict()
        data['map_id'] = gis_map.map_id
        data['layers'] = GisLayerSerializer(gis_map.gislayer_set.all(), many=True).data

        return self.success_response(data=data)
