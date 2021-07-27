from paho.mqtt import publish

import xmltodict
import json

xxx = '<MSG><META><SNDR>FIMS</SNDR><RCVR/><SEQN>84</SEQN><DDTM>20201102092901</DDTM><TYPE>DFOE</TYPE><STYP>DFIE</STYP><SORC/><MGID>104ad6e1-3078-476f-9474-ddedd7718c9a</MGID><RMID/><APOT>ZUGY</APOT></META>' \
      '<DFLT>' \
      '<FLID>17063</FLID>' \
      '<STAT>BOR</STAT>' \
      '<BORT>20220103124500</BORT>' \
      '</DFLT></MSG>'


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    topic = 'iis/bore'

    publish.single(topic, xxx, qos=0, hostname='127.0.0.1', auth={'username': 'admin', 'password': 'admin'},
                   keepalive=80, client_id='123')


publish_mq_message(xxx)
# def xml_to_dict(xml_data):
#     '''
#     xml to dict
#     :param xml_data:
#     :return:
#     '''
#     result = xmltodict.parse(xml_data)
#     print(result)
#     return result
#
#
# xml_to_dict(xxx)
