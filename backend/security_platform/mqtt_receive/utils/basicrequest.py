"""初始基础请求事件

Examples:
    publish_data = PublishData().get_data()
"""
import uuid
import datetime
from collections import OrderedDict

from security_platform.utils.commen import datetime_to_str


class PublishData:

    topic = None
    recv_platform = None

    def get_head(self):
        head = OrderedDict()
        head['service_code'] = f'SMP_{self.get_recv_platform()}_DEVICE_REQUEST'
        head['version'] = 1.8
        head['sender_platform'] = 'SMP'
        head['sender_sys'] = 'SMP'
        head['receiver_platform'] = self.get_recv_platform()
        head['receiver_sys'] = self.get_recv_platform()
        head['session_id'] = str(uuid.uuid1()).replace('-', '')
        head['time_stamp'] = datetime_to_str(datetime.datetime.now(), '%Y%m%d%H%M%S')

        return head

    def get_body(self):
        return {'device_request': {'request_type': 1}}

    def get_publish_msg(self):
        return {'msg': {'head': self.get_head(), 'body': self.get_body()}}

    def get_topic(self):
        assert self.topic is not None, (
                "'%s' should either include a `model_class` attribute, "
                "or override the `get_model_class()` method." % self.__class__.__name__
        )

        return self.topic

    def get_recv_platform(self):
        assert self.get_recv_platform is not None, (
                "'%s' should either include a `model_class` attribute, "
                "or override the `get_model_class()` method." % self.__class__.__name__
        )

        return self.recv_platform


class ACSPublishData(PublishData):
    """门禁"""

    topic = 'acs/device/request'
    recv_platform = 'ACS'


class AccessCardPublishData(PublishData):
    """门禁通行证"""

    topic = 'acs/perinfomation/request'
    recv_platform = 'ACS'

    def get_body(self):
        return {'passcard_request': {'request_type': 1}}


class CMSPublishData(PublishData):
    """道口"""

    topic = 'cms/device/request'
    recv_platform = 'CMS'


class AISPublishData(PublishData):
    """围界"""

    topic = 'ais/device/request'
    recv_platform = 'AIS'


class FirePublishData(PublishData):
    """火灾"""

    topic = 'xfhz/device/request'
    recv_platform = 'XFHZ'


class ConcealPublishData(PublishData):
    """消防"""

    topic = 'ybbj/device/request'
    recv_platform = 'YBBJ'
