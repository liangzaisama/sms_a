#!/bin/bash

# 依赖软件 mysql, redis, 依赖包
# 安装前注意事项、manage文件和config文件配置好、迁移文件删除

function install {
  rpm -ivh ${rpm_paths}
}

function create_virtualenv {
  pip3 install virtualenv
  /usr/local/bin/virtualenv /home/.virtualenvs/SMS -p python3

}

function source_virtualenv {
  source /home/.virtualenvs/SMS/bin/activate

}

function install_requirements {
#  pip install -r /home/OPS/sms_compile/requirements.txt
  pip install --no-index -f /home/OPS/sms_wheel -r /home/OPS/sms_compile/requirements.txt

}

function create_db_and_user {
  mysql_user='root'
  mysql_pwd='ZhengXin123+'

  /usr/bin/mysql -u${mysql_user} -p${mysql_pwd} -e'create database security_platform_v2 charset=utf8;'
  /usr/bin/mysql -u${mysql_user} -p${mysql_pwd} -e'create user "sms" identified by "GyjcAb1@!#";'
  /usr/bin/mysql -u${mysql_user} -p${mysql_pwd} -e'grant all on security_platform_v2.* to "sms"@"%";'
  /usr/bin/mysql -u${mysql_user} -p${mysql_pwd} -e'flush privileges;'

}

function migrate {
  python /home/OPS/sms_compile/security_platform/manage.pyc makemigrations
  python /home/OPS/sms_compile/security_platform/manage.pyc migrate

}

function crontab_add {
  python /home/OPS/sms_compile/security_platform/manage.pyc crontab add

}

function cp_config_file {
  # bin文件
  cp /home/OPS/sms_compile/service/sms /usr/bin/sms;chmod 777 /usr/bin/sms

  # 开机启动文件
  cp /home/OPS/sms_compile/service/sms.service /usr/lib/systemd/system/sms.service

  # nginx配置文件
#  cp /home/OPS/sms_compile/service/nginx.conf /etc/nginx/nginx.conf

  # 服务配置文件
#  cp /home/OPS/sms_compile/service/sms.conf /etc/nginx/conf.d/sms.conf

#  mkdir -p /etc/nginx/logs  # nginx日志使用
}

function systemctl_execute {
  systemctl daemon-reload
  systemctl enable sms
  systemctl stop sms
  systemctl start sms
#  systemctl restart nginx

}

function config_alias {
   echo "alias cm='cd /home/OPS/sms_compile/security_platform;source /home/.virtualenvs/SMS/bin/activate'" >> /etc/profile
   source /etc/profile
}

function set_somaxconn {
   sysctl -w net.core.somaxconn=4000
   echo "net.core.somaxconn= 4000" >> /etc/sysctl.conf
}

function main {
  # 安装包
  install

  # 创建虚拟环境,安装依赖
  create_virtualenv
  source_virtualenv
  install_requirements

  # 创建数据库
  create_db_and_user

  # 迁移及定时任务
  migrate
  crontab_add

  # 设置somaxconn最大值
#  set_somaxconn

  # 创建环境变量
  config_alias

  # 拷贝配置文件
  cp_config_file

  # 启动配置服务
  systemctl_execute

}


# 获取当前目录下第一个SMS-*.rpm文件
rpm_paths=$(find /home/OPS -maxdepth 1 -name "SMS-*.rpm" |tail -1)

if [ -n "${rpm_paths}" ]; then
   echo "开始安装安保管理平台后端服务"
   main
else
   echo "rpm文件不存在无法安装"
fi
