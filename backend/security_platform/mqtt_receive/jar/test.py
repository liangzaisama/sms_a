"""
调用二所的esb javaSDK获取航班消息
"""
from jpype import *
from jpype._core import startJVM, shutdownJVM
from jpype._jvmfinder import getDefaultJVMPath


def java_code_decorator(func):

    def java_wrapper(*args, **kwargs):
        # 启动java虚拟机
        # 注意使用了-D选项指定了jar的目标位置
        startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=./ZhMqRevice.jar")

        func(*args, **kwargs)

        # 关闭虚拟机
        shutdownJVM()

    return java_wrapper


def handler_message(message):
    print(message)


@java_code_decorator
def run_java_code():
    # 加载自定义的java class
    JDClass = JClass("com.caacitc.consumer.EsbConsumerWithAutoAck")
    jd = JDClass()
    queue = jd.getListenerImplTest().getQueue()
    jd.main([])

    while True:
        ret = queue.take()
        print(ret)


if __name__ == '__main__':
    run_java_code()
