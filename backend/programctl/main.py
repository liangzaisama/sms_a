"""
程序执行文件
"""
import argparse
import logging

from execute import OptionExecute


# 添加命令行参数
parser = argparse.ArgumentParser(description='安保管理平台后端服务运行及配置脚本')

# 数据库
parser.add_argument('-cd', '--create-db-and-user', metavar='root_password', default=argparse.SUPPRESS,
                    help='创建数据库及用户配置,需要传递root用户的密码')

# 命令
parser.add_argument('-mg', '--migrate', default=argparse.SUPPRESS, action='store_true', help='迁移数据库')
parser.add_argument('-ca', '--crontab-add', default=argparse.SUPPRESS, action='store_true', help='创建定时任务')
parser.add_argument('-mm', '--makemigrations', default=argparse.SUPPRESS, action='store_true', help='创建迁移文件')
parser.add_argument('-cr', '--crontab-remove', default=argparse.SUPPRESS, action='store_true', help='删除定时任务')

# 服务
parser.add_argument('-s', '--start', choices=['all', 'api', 'mq', 'ws', 'elk'], default=argparse.SUPPRESS,
                    help='开启服务 all:全部(不包含日志) api:接口 mq:MQ脚本 ws:websocket elk:日志系统')

parser.add_argument('-t', '--stop', choices=['all', 'api', 'mq', 'ws', 'elk'], default=argparse.SUPPRESS,
                    help='关闭服务 all:全部(不包含日志) api:接口 mq:MQ脚本 ws:websocket elk:日志系统')

parser.add_argument('-a', '--status', choices=['all', 'api', 'mq', 'ws', 'elk'], default=argparse.SUPPRESS,
                    help='查询服务 all:全部(不包含日志) api:接口 mq:MQ脚本 ws:websocket elk:日志系统')

parser.add_argument('-r', '--restart', choices=['all', 'api', 'mq', 'ws', 'elk'], default=argparse.SUPPRESS,
                    help='重启服务 all:全部(不包含日志) api:接口 mq:MQ脚本 ws:websocket elk:日志系统')


def main(command_args=None):
    """入口函数"""
    if command_args is None:
        command_args = vars(parser.parse_args())

    if command_args:
        try:
            OptionExecute(command_args).dispatch()
        except Exception:
            logging.error('程序执行失败', exc_info=True)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
