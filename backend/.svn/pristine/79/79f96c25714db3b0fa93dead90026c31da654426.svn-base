"""处理消息的相关进程类

进程类均继承自Process类，增加process_type属性表面自身的类型
"""
import os
from multiprocessing import Process

from jpype._core import startJVM
from jpype._jvmfinder import getDefaultJVMPath

from esb.esb_receive import receive_msg_from_esb
from esb.esb_publish import send_msg_to_esb


class ProcessTypeEnum:
    """进程类型枚举"""
    ESB_RECEIVE = 'ER'
    ESB_PUBLISH = 'EP'
    MQ_WORKER = 'MW'


class CustomProcess(Process):
    """自定义进程"""

    process_type = None

    @classmethod
    def get_process_type(cls):
        """获取进程类型"""
        assert cls.process_type is not None, (
            "'%s' should either include a `process_type` attribute, "
            "or override the `get_process_type()` method." % cls.__name__
        )
        return cls.process_type


class EsbMsgProcess(CustomProcess):
    """esb消息处理类

    增加自动加载java虚拟机
    """
    def start_jvm(self):
        """开启java虚拟机"""
        startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % (os.getcwd() + "/jar/ZhMqRevice.jar"))

    def _run(self):
        raise NotImplementedError('method _run() must be Implemented.')

    def run(self):
        self.start_jvm()
        self._run()


class EsbReceiveProcess(EsbMsgProcess):
    """收取航班系统esb消息进程"""

    process_type = ProcessTypeEnum.ESB_RECEIVE

    def _run(self):
        receive_msg_from_esb()


class EsbPublishProcess(EsbMsgProcess):
    """发送消息到航班系统进程"""

    process_type = ProcessTypeEnum.ESB_PUBLISH

    def _run(self):
        send_msg_to_esb()


class MsgWorkerProcess(CustomProcess):
    """其他子系统消息处理进程"""

    process_type = ProcessTypeEnum.MQ_WORKER
