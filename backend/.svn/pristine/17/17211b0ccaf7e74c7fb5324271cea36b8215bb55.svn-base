#!/bin/bash
#The index 30 days ago
LAST_DATA=`date -d "30 days ago" "+%Y.%m.%d"`
time=`date +"%Y-%m-%d %H:%M:%S"`
#ip=`ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"​ | xargs -n 1 2>/dev/null | head -1`
ip=192.168.21.126
curl -s -XGET http://$ip:9200/_cat/indices?v | grep $LAST_DATA | awk '{print $3}'>/home/admin/Desktop/ELK/scripts/index_name.log
for index_name in `cat /home/admin/Desktop/ELK/scripts/index_name.log` 
do
    curl -XDELETE  http://$ip:9200/$index_name
    if [ $? -eq 0 ];then
          echo $time"-->del $index_name log success.." >> /home/admin/Desktop/ELK/scripts/es-index-sucess-clear.log
    else
          echo $time"-->del $index_name log fail.." >> /home/admin/Desktop/ELK/scripts/es-index-fail-clear.log
    fi
done

