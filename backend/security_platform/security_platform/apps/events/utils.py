"""安保事件模块工具函数

HistoryStatistics、EventStatistics 事件统计枚举类
"""

from security_platform import TextChoices


class HistoryStatistics(TextChoices):
    """历史统计字段枚举"""
    DATE = 'date', '日期'
    MONTH = 'month', '月份'
    DATE_FORMAT = '%Y-%m-%d', '日期格式'
    MONTH_FORMAT = '%Y-%m', '月份格式'
    COUNT = 'count', '数量'


class EventStatistics(TextChoices):
    """事件统计字段枚举"""
    ALARM_TYPE = 'alarm_type', '报警类型'
    BELONG_SYSTEM = 'belong_system', '所属系统'
    PRIORITY = 'priority', '事件等级'
    ID = 'id', '事件id'
    PTR_ID = 'alarmevent_ptr_id', '事件id'
    COUNT = 'count', '数量'
