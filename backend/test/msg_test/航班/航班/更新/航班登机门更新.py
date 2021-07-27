from paho.mqtt import publish

import xmltodict
import json

xxx = """
<MSG>
    <META>
        <SNDR>FIMS</SNDR>
        <RCVR/>
        <SEQN>84</SEQN>
        <DDTM>20201102092901</DDTM>
        <TYPE>DFOE</TYPE>
        <STYP>DFIE</STYP>
        <SORC/>
        <MGID>104ad6e1-3078-476f-9474-ddedd7718c9a</MGID>
        <RMID/>
        <APOT>ZUGY</APOT>
    </META>
    <DFLT>
        <FLID>17063</FLID>
        <AFID/>
        <FFID>CA-8811T-20201102080000-D</FFID>
        <AWCD>CA</AWCD>
        <FLNO>8812T</FLNO>
        <FEXD>20201102</FEXD>
        <FIMD>20201102</FIMD>
        <FLIO>D</FLIO>
        <BAPT>KWE</BAPT>
        <FLTK>W/Z</FLTK>
        <FATT>DOM</FATT>
        <MFID/>
        <MFFI/>
        <CONT>1</CONT>
        <PROX>210</PROX>
        <CFTP>DHC7</CFTP>
        <CFNO>B-10GE</CFNO>
        <STAT/>
        <MSTA/>
        <ABST/><ABRS/>
        <IARS/>
        <BORT/>
        <MBOR/>
        <TBRT/>
        <MTBR/>
        <LBDT/>
        <MLBD/>
        <POKT/>
        <MPOK/>
        <APOT/>
        <VIP>0</VIP>
        <SFLG/>
        <PAST/>
        <AIRL>
            <ARPT>
                <APNO>1</APNO>
                <APCD>KWE</APCD>
                <FPTT>20201102080000</FPTT>
                <FETT>20201102080000<FETT/>
                <FRTT>20201102080000<FRTT/>
                <FPLT/>
                <FELT/>
                <FRLT/>
                <APAT>DOM</APAT>
                <FLAG/>
            <APRT/>
            <APRS/>
            </ARPT>
            <ARPT>
                <APNO>2</APNO>
                <APCD>PEK</APCD>
                <FPTT/><FETT/>
                <FRTT/>
                <FPLT>20201102100000</FPLT>
                <FELT>20201102100000<FELT/>
                <FRLT>20201102100000<FRLT/>
                <APAT>DOM</APAT>
                <FLAG/>
            <APRT/>
            <APRS/>
            </ARPT>
        </AIRL>
            <BLLS/>
            <EXNO/><CHLS/>
            <CKLS><FCES/>
            <FCEE/><FCRS/>
            <FCRE/><MCES/>
            <MCEE/><MCRS/>
            <MCRE/><FCDP/>
            <MCDP/></CKLS>
            <STLS/><TMCD>
            <NMCD>T1</NMCD>
            <JMCD/></TMCD>
            <RWAY/>
    </DFLT>
</MSG>
"""

xxx = '<MSG><META><SNDR>FIMS</SNDR><RCVR/><SEQN>84</SEQN><DDTM>20201102092901</DDTM><TYPE>DFOE</TYPE><STYP>DFIE</STYP><SORC/><MGID>104ad6e1-3078-476f-9474-ddedd7718c9a</MGID><RMID/><APOT>ZUGY</APOT></META><DFLT><FLID>17063</FLID><AFID/><FFID>CA-8811T-20201102080000-D</FFID><AWCD>CA</AWCD><FLNO>8812T</FLNO><FEXD>20201102</FEXD><FIMD>20201102</FIMD><FLIO>D</FLIO><BAPT>KWE</BAPT><FLTK>W/Z</FLTK><MFID/><MFFI/><CONT>1</CONT><PROX>210</PROX><CFTP>DHC7</CFTP><CFNO>B-10GE</CFNO><STAT/><MSTA/><ABST/><ABRS/><IARS/><BORT/><MBOR/><TBRT/><MTBR/><LBDT/><MLBD/><POKT/><MPOK/><APOT/><VIP>0</VIP><SFLG/><PAST/>' \
      '<GTLS>' \
          '<GATE>' \
              '<GTNO>17255</GTNO>' \
              '<ID>1997</ID>' \
              '<CODE>104</CODE>' \
              '<GTAT/>' \
              '<ESTR>20210917104800</ESTR>' \
              '<EEND>20210917112900</EEND>' \
              '<RSTR>20210917112900</RSTR>' \
              '<REND>20210917112900</REND>' \
              '<BTSC>T1</BTSC>' \
          '</GATE>' \
          '<GATE>' \
              '<GTNO>17255</GTNO>' \
              '<ID>1998</ID>' \
              '<CODE>104</CODE>' \
              '<GTAT/>' \
              '<ESTR>20280917104800</ESTR>' \
              '<EEND>20280917112900</EEND>' \
              '<RSTR>20280917112900</RSTR>' \
              '<REND>20280917112900</REND>' \
              '<BTSC>T1</BTSC>' \
          '</GATE>' \
      '</GTLS>'\
      '<EXNO/><CHLS/><CKLS><FCES/><FCEE/><FCRS/><FCRE/><MCES/><MCEE/><MCRS/><MCRE/><FCDP/><MCDP/></CKLS><RWAY/></DFLT></MSG>'


def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    topic = 'iis/gtls'

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
