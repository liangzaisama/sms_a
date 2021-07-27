"""
态势资源工具函数
"""
import datetime
from collections import OrderedDict


def current_time_transform(datetime_):
    """当前时间转化

    转化时间为了人数统计方便聚合查询时使用

    Args:
        datetime_: 转化的datetime对象

    Returns：
        转化后的datetime时间对象
        3种时间情况
        整点时间，取本身时间值
        非整点时间，取本身时间下个小时值
        超过23点的时间数据处理为23点59分59秒
    """
    statistical_kwargs = OrderedDict(
        year=datetime_.year,
        month=datetime_.month,
        day=datetime_.day,
        hour=datetime_.hour
    )

    if datetime_.minute != 0 or datetime_.second != 0 or datetime_.microsecond != 0:
        # 非整点时间

        if datetime_.hour != 23:
            statistical_kwargs['hour'] += 1
        else:
            # 24点 == 23点59分59秒
            statistical_kwargs['minute'] = 59
            statistical_kwargs['second'] = 59

    return datetime.datetime(**statistical_kwargs)
