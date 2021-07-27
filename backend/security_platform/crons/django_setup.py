"""django环境加载

方便使用orm模型类等
"""
import os
import sys

import django

# 命令行执行时，需要该导包路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from manage import set_django_module
    set_django_module()
    django.setup()

    from django.db import connection

    from events import models as event_model
    from configurations.models import SystemConfig
    from situations.models import FlightInfo, PassageWayCarPassThrough
    from security_platform import cron_logger as logger
    from security_platform.utils.commen import redis_lock_factory
except ImportError:
    raise ImportError("Couldn't import DJANGO_SETTINGS_MODULE")
