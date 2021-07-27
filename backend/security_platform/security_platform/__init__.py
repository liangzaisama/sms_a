import os
import logging
import configparser

import pymysql

from security_platform.utils.enums import TextChoices, IntegerChoices
from security_platform.utils.response_msg import ERROR_MAP, RET, ErrorType

pymysql.version_info = (1, 4, 6, 'final', 0)
pymysql.install_as_MySQLdb()

logger = logging.getLogger('django')
cron_logger = logging.getLogger('cron')
receive_logger = logging.getLogger('receive')

config_parser = configparser.ConfigParser()
config_parser.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'))
