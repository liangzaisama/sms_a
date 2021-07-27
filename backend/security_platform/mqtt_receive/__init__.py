"""
多进程MQ消息接收处理程序

消息对接方式
视频监控：内部MQ直接对接
视频分析：内部MQ直接对接
门禁：内部MQ直接对接
道口: 内部MQ直接对接
隐蔽报警：预计设备走MQ，报警走MQ或视频监控平台
消防：预计设备走MQ，报警走MQ或视频监控平台
围界：设备走MQ，报警消息走视频监控平台(需要摄像机的图)
"""
__title__ = 'Mqtt Receive'
__version__ = '1.0.0'
__author__ = 'lucas lwl'

# Version synonym
VERSION = __version__
