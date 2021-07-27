"""
django相关命令执行
"""
import os


class DjangoCommandExecute:
    """django命令执行"""

    def __init__(self, manage_file_path):
        self.manage_file_path = manage_file_path

    def makemigrations(self):
        """生成迁移"""
        os.system(f'python {self.manage_file_path} makemigrations')

    def migrate(self):
        """执行迁移"""
        os.system(f'python {self.manage_file_path} migrate')

    def crontab_add(self):
        """定时任务增加"""
        os.system(f'python {self.manage_file_path} crontab add')

    def crontab_remove(self):
        """定时任务移除"""
        os.system(f'python {self.manage_file_path} crontab remove')
