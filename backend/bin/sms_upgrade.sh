#!/bin/bash

function copy_old_code {
  cp -rf /home/OPS/sms_compile ${bak_paths}
  echo '重命名sms_compile完成'

}

function update_code {
  rpm -ivhF ${rpm_paths}
  echo '更新代码完成'

}

function copy_old_config {
  \cp -f "${bak_paths}/security_platform/config.ini" /home/OPS/sms_compile/security_platform/config.ini
  \cp -f "${bak_paths}/security_platform/manage.pyc" /home/OPS/sms_compile/security_platform/manage.pyc
  \cp -f "${bak_paths}/security_platform/mqtt_receive/settings.pyc" /home/OPS/sms_compile/security_platform/mqtt_receive/settings.pyc

  echo '复制配置文件完成'
}

function copy_old_migration {
  # 删除新的迁移文件
  rm -rf /home/OPS/sms_compile/security_platform/security_platform/apps/configurations/migrations
  rm -rf /home/OPS/sms_compile/security_platform/security_platform/apps/situations/migrations
  rm -rf /home/OPS/sms_compile/security_platform/security_platform/apps/devices/migrations
  rm -rf /home/OPS/sms_compile/security_platform/security_platform/apps/events/migrations
  rm -rf /home/OPS/sms_compile/security_platform/security_platform/apps/operations/migrations
  rm -rf /home/OPS/sms_compile/security_platform/security_platform/apps/users/migrations

  # 复制历史的迁移文件
  cp -rf "${bak_paths}/security_platform/security_platform/apps/configurations/migrations" /home/OPS/sms_compile/security_platform/security_platform/apps/configurations/migrations
  cp -rf "${bak_paths}/security_platform/security_platform/apps/situations/migrations" /home/OPS/sms_compile/security_platform/security_platform/apps/situations/migrations
  cp -rf "${bak_paths}/security_platform/security_platform/apps/devices/migrations" /home/OPS/sms_compile/security_platform/security_platform/apps/devices/migrations
  cp -rf "${bak_paths}/security_platform/security_platform/apps/events/migrations" /home/OPS/sms_compile/security_platform/security_platform/apps/events/migrations
  cp -rf "${bak_paths}/security_platform/security_platform/apps/operations/migrations" /home/OPS/sms_compile/security_platform/security_platform/apps/operations/migrations
  cp -rf "${bak_paths}/security_platform/security_platform/apps/users/migrations" /home/OPS/sms_compile/security_platform/security_platform/apps/users/migrations

  echo '替换迁移文件完成'

}

function migrate {
  python /home/OPS/sms_compile/security_platform/manage.pyc makemigrations
  python /home/OPS/sms_compile/security_platform/manage.pyc migrate
}

function source_virtualenv {
  source /home/.virtualenvs/SMS/bin/activate

}

function restart_server {
  systemctl stop sms
  systemctl start sms

}

function move_old_file {
  mkdir -p /home/OPS/bak
  mkdir -p /home/OPS/rpm
  mv ${bak_paths} /home/OPS/bak/
  mv /home/OPS/SMS*.rpm /home/OPS/rpm/

}

function api_test {
  sleep 3
  sms -a all
  sleep 1
  curl http://127.0.0.1/api/version

}

function crontab_add {
  python /home/OPS/sms_compile/security_platform/manage.pyc crontab add

}

function main {
  # 拷贝历史代码
  copy_old_code

  # 更新代码
  update_code

  # 拷贝配置文件/迁移文件
  copy_old_config
  copy_old_migration

  # 重新执行迁移
  source_virtualenv
  migrate

  # 增加定时任务
#  crontab_add

  # 重启服务
  restart_server

  # 将文件归档
  move_old_file
  api_test
}

# 获取当前目录下第一个SMS-*.rpm文件
rpm_paths=$(find /home/OPS -maxdepth 1 -name "SMS-*.rpm" |tail -1)

time=$(date "+%Y-%m-%d_%H:%M:%S")
bak_paths="/home/OPS/sms_compile_bak_${time}"

if [ -n "${rpm_paths}" ]; then
   echo "开始更新安保管理平台后端服务"
   main
else
   echo "rpm文件不存在无法更新"
fi
