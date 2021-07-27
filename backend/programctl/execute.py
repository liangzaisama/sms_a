"""
选项执行类
"""
from enums import DatabaseOptionEnum, DjangoCommandOptionEnum, ServerNameEnum, ServerOptionEnum
from factory import ServerFactory, DatabaseManagerFactory, DjangoCommandExecuteFactory, config_parser


class OptionExecute:
    """操作选项执行分发类"""

    def __init__(self, command_args):
        self.option = next(iter(command_args))
        self.param_value = command_args[self.option]

    def handel_not_found(self):
        """未找到执行的函数时调用"""
        raise AttributeError('未找到执行函数')

    def get_handler_by_factory_class(self, class_obj):
        """从对象获取执行函数"""
        obj = class_obj.create_object(self.param_value)
        handler = getattr(obj, self.option, self.handel_not_found)
        return handler

    def all_server_redispatch(self):
        """操作所有服务时重新进行分发"""
        for server_name in [
            ServerNameEnum.MQ_SERVER_NAME.value,
            ServerNameEnum.WS_SERVER_NAME.value,
            ServerNameEnum.API_SERVER_NAME.value,
        ]:
            self.param_value = server_name
            self.dispatch()

    def get_handler_and_kwargs(self):
        """获取执行函数及其参数"""
        handler_kwargs = {}

        if self.option in DatabaseOptionEnum.values():
            handler_kwargs['db_name'] = config_parser.get('MYSQL', 'MYSQL_NAME')
            handler_kwargs['username'] = config_parser.get('MYSQL', 'MYSQL_USER')
            handler_kwargs['password'] = config_parser.get('MYSQL', 'MYSQL_PASSWORD')
            class_obj = DatabaseManagerFactory()

        elif self.option in DjangoCommandOptionEnum.values():
            class_obj = DjangoCommandExecuteFactory()

        elif self.option in ServerOptionEnum.values():
            class_obj = ServerFactory()

        else:
            raise TypeError(f'不存在的操作选项:{self.option}')

        handler = self.get_handler_by_factory_class(class_obj)
        return lambda: handler(**handler_kwargs)

    def dispatch(self):
        """分发操作选项"""
        is_server_option = self.option in ServerOptionEnum.values()
        is_all_server_name = self.param_value == ServerNameEnum.ALL_SERVER_NAME.value

        if is_server_option and is_all_server_name:
            return self.all_server_redispatch()

        handler = self.get_handler_and_kwargs()
        handler()
