"""
工厂类
"""
import os

from enums import ServerNameEnum
from database import DatabaseManager
from command import DjangoCommandExecute
from server import ApiServer, MqReceiveServer, WebsocketServer, ELKServer
from utils import config_parser, config_file_path, app_file_path, base_dir, file_format, elk_base_dir


class Factory:
    """抽象工厂类"""

    def create_object(self, param_value):
        """创建对象"""
        raise NotImplementedError('create_object must be implemented')


class DatabaseManagerFactory(Factory):
    """数据库工厂类"""

    def create_object(self, param_value):
        return DatabaseManager(config_parser.get('MYSQL', 'MYSQL_HOST'),
                               int(config_parser.get('MYSQL', 'MYSQL_PORT')),
                               param_value)


class DjangoCommandExecuteFactory(Factory):
    """django命令工厂类"""

    def create_object(self, param_value):
        return DjangoCommandExecute(os.path.join(base_dir, f'security_platform/manage{file_format}'))


class ServerFactory(Factory):
    """服务工厂类"""

    def create_object(self, param_value):
        if param_value == ServerNameEnum.API_SERVER_NAME.value:
            obj = ApiServer(config_file_path)
        elif param_value == ServerNameEnum.MQ_SERVER_NAME.value:
            obj = MqReceiveServer(os.path.join(base_dir, f'security_platform/mqtt_receive/main{file_format}'))
        elif param_value == ServerNameEnum.WS_SERVER_NAME.value:
            obj = WebsocketServer(app_file_path)
        elif param_value == ServerNameEnum.elk_server_name.value:
            obj = ELKServer(os.path.join(elk_base_dir, f'ELK/scripts/elk.sh'))
        else:
            raise TypeError(f'不存在的服务名称:{param_value}')

        return obj
