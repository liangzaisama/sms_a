"""日志切割脚本

本脚本未使用：原则上是一天分割一次，使用时会导致django日志文件被删除导致django日志无法继续写入
解决办法：让日志处理器定时旋转，以写入新的日志文件

当前使用自带的TimedRotatingFileHandler进行每天自动切割
"""
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LogCutter:
    """日志分割器

    Attributes:
        src_log_path: 日志来源的绝对路径，默认为None, 将使用默认配置
        dest_log_path: 日志切割备份后的绝对路径，默认为None, 将使用默认配置
        expire_days: 日志的过期天数，默认30天
        backup_path: 根据当前日期生成的日志切割后的存储路径
    """

    def __init__(self, src_log_path=None, dest_log_path=None, expire_days=30):
        self.src_log_path = src_log_path or os.path.join(BASE_DIR, 'logs')
        self.dest_log_path = dest_log_path or '/var/log/sms'
        self.expire_days = expire_days
        self.backup_path = os.path.join(self.dest_log_path, str(self.current_date))

    @property
    def current_date(self):
        """获取当前日期"""
        if not hasattr(self, '_current_date'):
            self._current_date = datetime.now().date()

        return self._current_date

    def mkdir(self):
        """创建var下面的文件夹"""
        os.makedirs(self.backup_path, exist_ok=True)

    def backup(self):
        """logs下面的文件移到var下面"""
        for file in os.listdir(self.src_log_path):
            if '.log' in file:
                file_path = os.path.join(self.src_log_path, file)
                os.system(f'cp -rf {file_path} {self.backup_path};rm -rf {file_path}')

    def delete(self):
        """删除历史日志备份"""
        for log_dir in os.listdir(self.dest_log_path):
            try:
                file_date = datetime.strptime(log_dir, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                # 非日期命名的文件夹跳过
                continue

            if (self.current_date - file_date).days > self.expire_days:
                shutil.rmtree(os.path.join(self.dest_log_path, log_dir))

    def cut(self):
        """进行日志切割"""
        self.mkdir()
        self.backup()
        self.delete()


if __name__ == '__main__':
    c = LogCutter(dest_log_path='/Users/lwl/Desktop/work/svn_/SMS/backend/security_platform/logs/sms/', expire_days=1)
    c.cut()
