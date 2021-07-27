import os
import sys
sys.path.insert(0, '/Users/liangzaisama/Desktop/sms/backend/test/msg_test/')
# sys.path.insert(0, '/Users/lwl/Desktop/python资料/源代码/pratice/test/msg_test/')
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir))
print(sys.path)
from backend.test.msg_test.分析.人数统计实时 import test as rere
from backend.test.msg_test.分析.人数统计实时 import test as renshutongji
from backend.test.msg_test.分析.排队实时 import test as paidui
from backend.test.msg_test.分析.密度报警 import test as midu
from backend.test.msg_test.分析.姿态 import test as zitai
from backend.test.msg_test.分析.布控抓拍 import test as zhuapai
from backend.test.msg_test.分析.布控报警 import test as zhuapaibaojing
from backend.test.msg_test.分析.道口车辆 import test as daokouche
from backend.test.msg_test.分析.围界报警 import test as weijiebaojing

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


f_li = [
    # renshutongji,
    # paidui,
    # midu,
    # zitai,
    # zhuapai,
    zhuapaibaojing,
    # daokouche,
    weijiebaojing,
]


def main():
    executor = ProcessPoolExecutor(max_workers=1)
    for func in f_li:
        try:
            future = executor.submit(func, hostname='192.168.21.97', sep=0.1, port=1883)
            # future = executor.submit(func, hostname='192.168.20.99', sep=0.1, port=1883)
            future = executor.submit(func, sep=1)
        except Exception as e:
            print(e)

    # 1s 10条


if __name__ == '__main__':
    main()
