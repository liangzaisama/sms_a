"""服务接口
# 1. 开启服务
# 2. 关闭服务
# 3. 重启服务
"""
import os
import time

from utils import config_parser


class GenericServer:
    """通用服务"""

    def __init__(self, execute_file_path):
        self.execute_file_path = execute_file_path
        self.chdir = os.path.split(execute_file_path)[0]

    def start(self):
        """开启服务"""
        raise NotImplementedError('start must be implemented')

    def stop(self):
        """关闭服务"""
        os.system("ps x|grep %s|grep -v grep |awk '{print $1}'|xargs kill -9" % self.execute_file_path)

    def restart(self):
        """重启服务"""
        self.stop()
        self.start()

    def status(self):
        """查询服务"""
        os.system("ps x|grep %s|grep -v grep" % self.execute_file_path)


class ApiServer(GenericServer):
    """后端接口服务"""

    def start(self):
        os.system(f'cd {self.chdir};uwsgi --ini {self.execute_file_path}')

    def restart(self):
        """重启服务"""
        self.stop()
        time.sleep(1)
        self.start()


class MqReceiveServer(GenericServer):
    """MQ收消息服务"""

    def start(self):
        os.system(f'cd {self.chdir};nohup python {self.execute_file_path} > /dev/null 2>&1 &')


class WebsocketServer(GenericServer):
    """websocket服务"""

    def start(self):
        ws_workers = config_parser.get('WEBSOCKET', 'WORKERS')
        ws_port = config_parser.get('WEBSOCKET', 'PORT')

        start_command = f"nohup hypercorn security_platform.asgi:application -b 0.0.0.0:{ws_port} -w {ws_workers} --error-log logs/hypercorn.log > /dev/null 2>&1 &"
        os.system(f'cd {self.chdir};{start_command}')

    def stop(self):
        """关闭服务"""
        os.system("ps x|grep hypercorn|grep -v grep |awk '{print $1}'|xargs kill -9")

    def status(self):
        """查询服务"""
        os.system("ps x|grep hypercorn|grep -v grep")


class ELKServer(GenericServer):
    """elk日志系统服务"""

    def start(self):
        os.system(f'cd {self.chdir};bash {self.execute_file_path} start')

    def stop(self):
        os.system(f'cd {self.chdir};bash {self.execute_file_path} stop')

    def status(self):
        os.system(f'cd {self.chdir};bash {self.execute_file_path} start')
