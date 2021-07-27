import copy
import datetime
import json
import os
import sys
import socket
import time
from collections import OrderedDict, Counter
from functools import reduce
from threading import local

from websocket import create_connection, WebSocketException

import django

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(base_dir))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "security_platform.settings.%s" % 'dev')
# sys.path.insert(0, os.path.join(base_dir+'/security_platform'))

# try:
#     from manage import set_django_module
#
#     set_django_module()
#     django.setup()
#
#     from security_platform import logger, config_parser
#     from settings import dev
#     from devices.models import DeviceInfo
#     # from core.ws import ws_connections
# except Exception as e:
#     raise ImportError("Couldn't import DJANGO_SETTINGS_MODULE")

test_list = [4, 3, 2, 1, 5, 3, 6]


def bubble_sort(test_list):
    length = len(test_list)
    # 第一级遍历
    for index in range(length):
        # 标志位
        flag = True
        # 第二级遍历
        for j in range(1, length - index):
            if test_list[j - 1] > test_list[j]:
                # 交换两者数据，这里没用temp是因为python 特性元组。
                test_list[j - 1], test_list[j] = test_list[j], test_list[j - 1]
                flag = False
            if flag:
                # 没有发生交换，直接返回list
                return test_list
    return test_list


test_list2 = [4, 3, 2, 1, 5, 3, 6]


def selection_sort(test_list):
    lenth = len(test_list)
    for i in range(0, lenth):
        min = i
        for j in range(i + 1, lenth):
            if test_list[j] < test_list[min]:
                min = j
                test_list[min], test_list[i] = test_list[i], test_list[min]

    return test_list


def quick_sort(list):
    less = []
    pivotList = []
    more = []
    # 递归出口
    if len(list) <= 1:
        return list
    else:
        # 将第一个值做为基准
        pivot = list[0]
        for i in list:
            # 将比急转小的值放到less数列
            if i < pivot:
                less.append(i)
            # 将比基准打的值放到more数列
            elif i > pivot:
                more.append(i)
            # 将和基准相同的值保存在基准数列
            else:
                pivotList.append(i)
        # 对less数列和more数列继续进行排序
        less = quick_sort(less)
        more = quick_sort(more)
        a = less + pivotList + more
        return less + pivotList + more


# class WebsocketConnectionWrapper:
#     """websocket连接包装器
#
#     Attributes:
#         connection: 当前websocket连接
#         ws_url: 当前websocket连接地址
#         max_age: websocket连接持久时间
#         close_at: 当前websocket连接关闭时间
#     """
#
#     def __init__(self, ws_url):
#         """初始化
#
#         Args:
#             ws_url: websocket连接地址
#         """
#         self.connection = None
#         self.ws_url = ws_url
#         self.max_age = 600
#         self.close_at = None
#
#     def connect(self):
#         """连接websocket
#
#         连接成功后设置连接的关闭时间, layer阻塞时可能会很久，所以建议使用异步执行websocket
#
#         Raises:
#             WebsocketError: 连接失败时抛出异常
#         """
#         try:
#             self.connection = create_connection(self.ws_url, timeout=self.max_age)
#         except (ConnectionError, socket.error, WebSocketException) as exc:
#             raise exc
#         else:
#             self.close_at = time.time() + (self.max_age - 30)
#
#     def close(self):
#         """关闭连接"""
#         if self.connection is not None:
#             try:
#                 self.connection.close()
#             except:
#                 pass
#             finally:
#                 self.connection = None
#
#     def reconnect_if_obsolete(self):
#         """超时重连"""
#         if self.connection is not None:
#             if self.close_at is not None and time.time() >= self.close_at:
#                 self.close()
#                 self.connect()
#
#     def ensure_connection(self):
#         """确保存在连接"""
#         if self.connection is None:
#             self.connect()
#
#     def __enter__(self):
#         """with调用时返回连接"""
#         self.reconnect_if_obsolete()
#         self.ensure_connection()
#
#         return self.connection
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """发送异常时关闭连接"""
#         if exc_type is None:
#             return None
#
#         logger.error('发送websocket消息失败:%s', exc_val)
#
#         self.close()
#         return True
#
#
# class WebsocketConnectionHandler:
#     """连接中介
#
#     Attributes:
#         _connections: websocket连接池，存储了不同进程使用的连接对象
#     """
#
#     def __init__(self):
#         self._connections = local()
#
#     def __getitem__(self, ws_url):
#         """通过websocket地址获取连接
#
#         实际是从自身维护的连接池中获取连接，如果没有连接则创建一个新的返回
#
#         Args:
#             ws_url: websocket连接地址
#
#         Returns:
#             跟地址对应的ws连接对象
#
#         Examples:
#             conn = ws_connections['event']
#         """
#         if hasattr(self._connections, ws_url):
#             return getattr(self._connections, ws_url)
#
#         conn = WebsocketConnectionWrapper(ws_url)
#         setattr(self._connections, ws_url, conn)
#         return conn
#
#     def __setitem__(self, key, value):
#         """设置连接到连接池"""
#         setattr(self._connections, key, value)
#
#     def __delitem__(self, key):
#         """连接池中删除连接"""
#         delattr(self._connections, key)
#
#
# ws_connections = WebsocketConnectionHandler()
# a = DeviceInfo.objects.get(id=1)
# ws_suffix = a.WS_URL_SUFFIX
# message = a.ws_message
# try:
#     ws_connection = ws_connections[os.path.join(
#         config_parser.get('WEBSOCKET', 'WEBSOCKET_ADDRESS'), ws_suffix
#     )]
#
#     message['publisher'] = True
#     message['send_time'] = str(datetime.datetime.now())
#
#     with ws_connection as conn:
#         conn.send(json.dumps(message))
# except Exception as exc:
#     logger.error(exc)


def quick_sort(test_list):
    less_list = []
    pivot_list = []
    more_list = []

    # 递归出口
    if len(test_list) <= 1:
        return test_list
    else:
        # 选定基准
        pivot = test_list[0]

        for i in test_list:
            # 将比基准小的值放入less队列
            if i < pivot:
                less_list.append(i)
            # 将比基准大的值放入more队列
            elif test_list > pivot:
                more_list.append(i)
            else:
                pivot_list.append(i)
        # 对less数列和more数列进行排序
        less_list = quick_sort(less_list)
        more_list = quick_sort(more_list)

        return less_list + pivot_list + more_list


a = '2.12345000000'
b = list(a)
# c = [i for i in b if i != '0']

print(b)
# print(c)
c = len(b)
for i in range(c):
    if b[-1] == '0' or b[-1] == '.':
        b.remove(b[-1])
print(b)
nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]


# class Solution:
#     def removeDuplicates(self, nums):
#         i = 0
#         while i < len(nums)-1:
#             if nums[i] == nums[i+1]:
#                 del nums[i+1]
#                 continue
#             i = i+1
#         print(len(nums))
#         return len(nums)
#
# a=Solution()
# b=a.removeDuplicates(nums=nums)
def test1(nums):
    i = 0
    while i < len(nums) - 1:
        if nums[i] == nums[i + 1]:
            del nums[i + 1]
            continue
        i += 1
    print(len(nums))
    return len(nums)


def test2(nums):
    for i in range(len(nums) - 1, 0, -1):
        if nums[i] == nums[i - 1]:
            del nums[i]
    print(nums)
    return len(nums)


test1(nums)
test2(nums)


def test3(nums):
    start = 0
    end = len(nums) - 1
    while start < end:
        nums[start], nums[end] = nums[end], nums[start]
        start += 1
        end -= 1
    print(nums)


test3(nums)


# node=[4,1,5,9]
# def deleteNode(node):
#     """
#     :type node: ListNode
#     :rtype: void Do not return anything, modify node in-place instead.
#     """
#
#     node.val = node.next.val
#     node.next = node.next.next
#

nums=[1,1,2,2,3,4,4,5,5]
Counter
def test4(nums):
    a=reduce(lambda x, y: x ^ y, nums)
    return reduce(lambda x, y: x ^ y, nums)
print(test4(nums))
s = "loveleetcode"
def test5(s):
    for i in s:
        if s.find(i)==s.rfind(i):
            return i
    return -1
print(test5(s))
a4 = [1, 2, [4, 5]]
b4=copy.copy(a4)
print(a4)
print(b4)
a4.append(3)
print(a4)
print(b4)
a4[2].append(3)
print(a4)
print(b4)
print('----------')
a4 = [1, 2, [4, 5]]
c4=copy.deepcopy(a4)
a4.append(3)
print(a4)
print(c4)
a4[2].append(3)
print(a4)
print(c4)
a='123'
b=list(a)
b[:]=b[::-1]
print(b)
c=list(a)
c.reverse()
print(c)
print(c.index('1'))

a='(){}[]'
def isValid( s) :
    """
    思路：
    方法：栈(入栈 出栈)
    """
    stack = []
    matchs = {')':'(', '}':'{', ']':'['}
    for ch in s:
        if ch in matchs.keys():
            if not(stack and matchs[ch] == stack.pop()):
                return False
        else:
            stack.append(ch)
    return not stack


isValid(a)

def fb(n):
    if n == 1 or n == 2:
        return 1
    return fb(n - 1) + fb(n - 2)

print(fb(7))