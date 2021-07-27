import xmltodict
from paho.mqtt import publish

data = """
<MSG>
    <META>
        <SNDR>IIS</SNDR>
        <RCVR></RCVR>
        <SEQN>1</SEQN>
        <DDTM>2010010223000</DDTM>
        <TYPE>BASE</TYPE>
        <STYP>APUE</STYP>
        <MGID>A20121220234816RE7A97855BA84fd5B</MGID>
        <RMID></RMID>
        <APOT>ZUUU</APOT>
    </META>
    <STND>         
        <CODE>A1</CODE>         
        <CNNM>A1机位</CNNM>         
        <ENNM>A1STAND</ENNM>         
        <REMT>Y</REMT>
        <HANG>Y</HANG>         
        <TMLC>A</TMLC>         
        <STUS>O</STUS>         
        <CTLV>E</CTLV>         
        <STGP>T1南区</STGP>         
        <SWID></SWID>         
        <SHGT></SHGT>         
        <MABS>2</MABS>        
        <DIGT></DIGT>         
        <DDGT>12</DDGT>         
        <FEPU>N</FEPU>     
        </STND>     
    <STND>         
        <CODE>B2</CODE>         
        <CNNM>B2机位</CNNM>         
        <ENNM>B2 STAND</ENNM>         
        <REMT>N</REMT>         
        <TMLC>B</TMLC>         
        <STUS>O</STUS>         
        <CTLV>E</CTLV>         
        <STGP>T1南区</STGP>         
        <SWID></SWID>         
        <SHGT></SHGT>         
        <MABS>2</MABS>         
        <DIGT></DIGT>         
        <DDGT>12</DDGT>         
        <FEPU>N</FEPU>     
    </STND> 
</MSG>
"""

def publish_mq_message(content):
    """
    发送消息
    :param topic 推送消息主题
    :param send_data 发送给算法的数据
    :param tag_sign 发送tag标识名称
    :return 发送结果
    """
    topic = 'iis/stie'

    publish.single(topic, content, qos=0, hostname='127.0.0.1',
        auth={'username': 'admin', 'password': 'admin'}, keepalive=80, client_id='123')


publish_mq_message(data)
# def xml_to_dict(data):
#     result = xmltodict.parse(data)
#     print(result)
#     return result
#
#
# xml_to_dict(data)
