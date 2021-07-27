"""
枚举类
"""
from enum import Enum


class GenericEnum(Enum):
    """通用枚举"""

    @classmethod
    def values(cls):
        """获取枚举列表"""
        return [str(i) for i in cls]

    def __str__(self):
        return str(self.value)


class DatabaseOptionEnum(GenericEnum):
    """数据库选项枚举"""
    CREATE = 'create_db_and_user'


class DjangoCommandOptionEnum(GenericEnum):
    """django命令枚举"""
    MIG = 'migrate'
    MAG = 'makemigrations'
    CRON_ADD = 'crontab_add'
    CRON_REMOVE = 'crontab_remove'


class ServerOptionEnum(GenericEnum):
    """服务操作枚举"""
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    STATUS = 'status'


class ServerNameEnum(GenericEnum):
    """服务名称枚举"""
    ALL_SERVER_NAME = 'all'
    API_SERVER_NAME = 'api'
    MQ_SERVER_NAME = 'mq'
    WS_SERVER_NAME = 'ws'
    ELK_SERVER_NAME = 'elk'
