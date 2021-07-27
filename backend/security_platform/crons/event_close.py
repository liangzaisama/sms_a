"""系统报警事件自动关闭

每分钟执行一次
事件关闭条件
0.自动上报
1.状态待处置
2.创建时间在60分钟以上
3.无工单流程
"""
from datetime import datetime, timedelta

from django_setup import logger, SystemConfig, connection, event_model, redis_lock_factory


def _close_expire_event(config_key, priority):
    """事件关闭"""
    diff_hours = SystemConfig.objects.get(config_key=config_key).config_value
    latest_time = datetime.now() - timedelta(hours=int(diff_hours))
    print(latest_time)

    execute_sql = f"""
        update tb_basic_alarm_event set event_state='{event_model.DeviceAlarmEvent.EventState.RELIEVED}' where id in (
            select ret.id from (
                select event.id from tb_basic_alarm_event event left join tb_event_work_sheet as sheet 
                on sheet.alarm_event_id=event.id 
                where event.event_type={event_model.AlarmEvent.EventType.DEVICE}
                and event.priority = {priority}
                and event.event_state='{event_model.DeviceAlarmEvent.EventState.UNDISPOSED}'
                and event.create_time < '{latest_time}'
                and sheet.id is null
            ) ret 
        );
    """

    with connection.cursor() as cursor:
        update_count = cursor.execute(execute_sql)
        if update_count:
            logger.info(f'关闭{priority}级报警事件%s个', update_count)


@redis_lock_factory('close_expire_event', 30)
def close_expire_event():
    """事件关闭"""
    _close_expire_event(SystemConfig.ConfigKey.EVENT_CLOSE_1, 1)
    _close_expire_event(SystemConfig.ConfigKey.EVENT_CLOSE_2, 2)
    _close_expire_event(SystemConfig.ConfigKey.EVENT_CLOSE_3, 3)
    _close_expire_event(SystemConfig.ConfigKey.EVENT_CLOSE_4, 4)


if __name__ == '__main__':
    close_expire_event()
