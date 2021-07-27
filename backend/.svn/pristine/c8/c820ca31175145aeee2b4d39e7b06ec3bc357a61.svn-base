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
    <BELT>         
        <ID>0606004</ID>         
        <CODE>A1</CODE>         
        <CNNM>A1</CNNM>         
        <ENNM>A1BELT</ENNM>         
        <ATTR>2401</ATTR>         
        <TMLC>A</TMLC>         
        <STUS>O</STUS>         
        <PROX>210</PROX>         
        <EXNO>5</EXNO>     
    </BELT>     
    <BELT>         
        <ID>0606005</ID>         
        <CODE>B2</CODE>         
        <CNNM>B2</CNNM>         
        <ENNM>B2BELT</ENNM>         
        <ATTR>2401</ATTR>         
        <TMLC>B</TMLC>         
        <STUS>O</STUS>         
        <PROX>210</PROX>         
        <EXNO>5</EXNO>     
    </BELT> 
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
    topic = 'iis/bldl'

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
