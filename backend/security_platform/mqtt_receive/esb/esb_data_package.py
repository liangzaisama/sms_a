"""对发送给esb的数据进行封装

esb_msg_package 数据封装类对象, 需要消息类型、子类型和消息体参数
Example:
    esb_msg_package.package_analysis_data(self.iis_type, self.iis_son_type, label)
"""
import uuid
import datetime
from collections import OrderedDict

from settings import settings


class EsbMsgPackage:
    """发送给esb数据封装"""

    COMMON_BASIC_REQUEST = 0
    FLIGHT_BASIC_REQUEST = 1
    ZUGY_BASIC_REQUEST = 2
    initial_requests_codes = settings.ESB_INITIAL_REQUEST_CODES

    def get_meta(self, msg_type, msg_son_type):
        """获取消息meta数据字典"""
        meta_data = OrderedDict()
        meta_data['SNDR'] = 'T3SIP'
        meta_data['RCVR'] = None
        meta_data['SEQN'] = None
        meta_data['DDTM'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        meta_data['TYPE'] = msg_type
        meta_data['STYP'] = msg_son_type
        meta_data['MGID'] = str(uuid.uuid1()).replace('-', '')
        meta_data['RMID'] = None
        meta_data['APOT'] = 'ZUGY'

        return meta_data

    def get_basic_request_data(self, msg_type, msg_son_type):
        """获取基础请求数据格式"""
        publish_msg = OrderedDict()
        publish_msg['META'] = self.get_meta(msg_type, msg_son_type)

        if msg_son_type in ('RQAP', 'RQAR', 'RQAW'):
            # 机场、原因
            publish_msg['RQST'] = None
        elif msg_son_type in ('RQGT', 'RQST', 'RQBL', 'RQCC'):
            # 资源
            publish_msg['RQST'] = OrderedDict()
            publish_msg['RQST']['BAPT'] = 'ZUGY'
        else:
            # 航班
            publish_msg['RQDF'] = OrderedDict()
            publish_msg['RQDF']['RQTP'] = None
            publish_msg['RQDF']['BAPT'] = 'ZUGY'

        return publish_msg

    @property
    def initial_request_data(self):
        """服务启动初始化时加载数据"""
        return [self.get_basic_request_data('REQE', code) for code in self.initial_requests_codes]

    def package_analysis_data(self, msg_type, msg_son_type, analysis_data):
        """封装视频分析数据"""
        publish_msg = OrderedDict()
        publish_msg['META'] = self.get_meta(msg_type, msg_son_type)
        publish_msg['INFO'] = analysis_data

        return publish_msg


esb_msg_package = EsbMsgPackage()
