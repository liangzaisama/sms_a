import os
import signal
import sys
import time


def time_consuming(func):
    def wrapper(*args, **kwargs):
        s = time.perf_counter()
        func(*args, **kwargs)
        e = time.perf_counter()
        print('use', e - s)
        return wrapper


def get_pid(name):
    """获取进程id"""
    print(name, os.getpid())


def exit_signal_handle(sig, _):
    """程序退出"""
    print(sig, os.getpid())
    sys.exit(0)


def catch_exit_signal():
    """捕获程序退出信号"""
    signal.signal(signal.SIGINT, exit_signal_handle)
    signal.signal(signal.SIGHUP, exit_signal_handle)
