import xmltodict
from paho.mqtt import publish


# data = """
# <MSG>
#     <META>
#         <SNDR>IIS</SNDR>
#         <RCVR></RCVR>
#         <SEQN>1</SEQN>
#         <DDTM>2010010223000</DDTM>
#         <TYPE>BASE</TYPE>
#         <STYP>APUE</STYP>
#         <MGID>A20121220234816RE7A97855BA84fd5B</MGID>
#         <RMID></RMID>
#         <APOT>ZUUU</APOT>
#     </META>
#     <DFLT> 
#         <FLID>96360</FLID> 
#         <FFID>9H-8464-20210409144000-A</FFID> 
#         <FLTK>W/Z</FLTK>
#          <FATT>DOM</FATT> 
#         <STLS> 
#             <STND>
#                  <STNO>1</GTNO> 
#                 <CODE>401#机位</CODE> 
#                  <ESTR>20210412100532</ESTR>
#                  <EEND>20210412110532</EEND> 
#                 <RSTR>20210412100532</RSTR>
#                  <REND></REND>
#                  <BTSC>T3</BTSC> 
#                  <CSSI>Y</CSSI> 
#             </STND> 
#         </STLS> 
#     </DFLT> 
# </MSG>
# """


data = '<MSG><META><SNDR>FIMS</SNDR><RCVR/><SEQN>84</SEQN><DDTM>20201102092901</DDTM><TYPE>DFOE</TYPE><STYP>DFIE</STYP><SORC/><MGID>104ad6e1-3078-476f-9474-ddedd7718c9a</MGID><RMID/><APOT>ZUGY</APOT></META>' \
       '<DFLT>' \
       '<FLID>96360</FLID>' \
       '<AFID/><FFID>CA-8811T-20201102080000-D</FFID>' \
       '<AWCD>CA</AWCD>' \
       '<FLNO>8811T</FLNO>' \
       '<FEXD>20201102</FEXD>' \
       '<FIMD>20201102</FIMD>' \
       '<FLIO>D</FLIO>' \
       '<BAPT>KWE</BAPT>' \
       '<FLTK>W/Z</FLTK>' \
       '<FATT>DOM</FATT>' \
      '<STLS>' \
          '<STND>' \
              '<CODE>401#机位</CODE>' \
              '<ESTR>20210412100532</ESTR>' \
              '<EEND>20210412110532</EEND>' \
              '<RSTR>20210412110532</RSTR>' \
              '<REND>20210412120532</REND>' \
              '<BTSC>T1</BTSC>' \
              '<CSSI></CSSI>' \
          '</STND>' \
      '</STLS>'\
      '<EXNO/><CHLS/><CKLS><FCES/><FCEE/><FCRS/><FCRE/><MCES/><MCEE/><MCRS/><MCRE/><FCDP/><MCDP/></CKLS><TMCD><NMCD>T1</NMCD><JMCD/></TMCD><RWAY/></DFLT></MSG>'


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    import json
    import random
    topic = 'iis/stls'
    content['MSG']['DFLT']['STLS']['STND']['CSSI'] = random.choices(['Y', None, 'Y'])[0]
    print(content)
    publish.single(topic, json.dumps(content), qos=1, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


def xml_to_dict(data):
    result = xmltodict.parse(data)
    return result

while True:
    publish_mq_message(xml_to_dict(data))
    import time
    time.sleep(5)
