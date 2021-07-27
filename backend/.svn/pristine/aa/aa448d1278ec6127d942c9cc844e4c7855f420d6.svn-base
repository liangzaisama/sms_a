"""
定时任务脚本，使用django_crontab执行
"""
import os
import sys

# 定时任务执行时，需要该导包路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from expire_delete import delete_expire_data
from event_close import close_expire_event
