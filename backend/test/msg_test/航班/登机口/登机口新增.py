import xmltodict
from paho.mqtt import publish

data = """<?xml version="1.0" encoding="UTF-8"?>
 <MSG>     
    <META>         
        <SNDR>IIS</SNDR>         
        <RCVR></RCVR>         
        <SEQN>1</SEQN>         
        <DDTM>20100103120000</DDTM>         
        <TYPE>BASE</TYPE>         
        <STYP>GTIE</STYP>        	
        <MGID>A20121220234816RE7A97855BA84fd5B</MGID>         
        <RMID></RMID>         
        <APOT>ZUUU</APOT>     
    </META>     
    <GATE>         
        <ID>0606003</ID>         
        <CODE>A1</CODE>         
        <CNNM>A1登机门</CNNM>         
        <ENNM>A1GATE</ENNM>         
        <ATTR>2401</ATTR>         
        <TMLC>A</TMLC>         
        <CRDC>A</CRDC>         
        <STUS>O</STUS>         
        <PROX>210</PROX>     
    </GATE> 
</MSG>
"""
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
    <GATE>         
        <ID>0606003</ID>         
        <CODE>A2</CODE>         
        <CNNM>A2登机门21</CNNM>         
        <ENNM>A2GATE</ENNM>         
        <ATTR>DOM</ATTR>         
        <TMLC>A</TMLC>         
        <CRDC>A</CRDC>         
        <STUS>O</STUS>         
        <PROX>210</PROX>     
    </GATE> 
    <GATE>         
        <ID>0606002</ID>         
        <CODE>A1</CODE>         
        <CNNM>A1登机门11</CNNM>         
        <ENNM>A1GATE</ENNM>         
        <ATTR>DOM</ATTR>         
        <TMLC>A</TMLC>         
        <CRDC>A</CRDC>         
        <STUS>O</STUS>         
        <PROX>210</PROX>     
    </GATE> 
    <GATE>         
        <ID>0606001</ID>         
        <CODE>A3</CODE>         
        <CNNM>A3登机门31</CNNM>         
        <ENNM>A3GATE</ENNM>         
        <ATTR>DOM</ATTR>         
        <TMLC>A</TMLC>         
        <CRDC>A</CRDC>         
        <STUS>O</STUS>         
        <PROX>210</PROX>     
    </GATE> 
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
    topic = 'iis/gtie'

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
