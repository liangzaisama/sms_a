#!/bin/bash
workdir=/home/admin/Desktop/ELK
LOG_HOME=$workdir/kibana-7.7.0-linux-x86_64/kibana.log
KB_START_SHELL=$workdir/kibana-7.7.0-linux-x86_64/bin/kibana
CONF_HOME=$workdir/logstash-7.7.0/conf
LS_START_SHELL=$workdir/logstash-7.7.0/bin/logstash
start() {
    if [ `ps aux|grep elasticsearch | grep -v grep|wc -l` -eq 0 ];then
        $workdir/elasticsearch-7.7.0/bin/elasticsearch -d
	echo $workdir
	if [ $? -eq 0 ];then
	    echo "start elasticsearch:" true
    	else
            echo "start elasticsearch:" false
	fi
    else
       echo "elasticsearch is running"
    fi
    sleep 5
    if [ `ps aux|grep logstash | grep -v grep|wc -l` -eq 0 ];then
        nohup $LS_START_SHELL -f $CONF_HOME > /dev/null 2>&1 &
        if [ $? -eq 0 ];then
            echo "start logstash:" true
        else
            echo "start logstash:" false
        fi
    else
       echo "logstash is running"
    fi
    sleep 10
    if [ `ps aux|grep kibana | grep -v grep|wc -l` -eq 0 ];then
        nohup $KB_START_SHELL > $LOG_HOME 2>&1 &
        if [ $? -eq 0 ];then
            echo "start kibana:" true
        else
            echo "start kibana:" false
        fi
    else
       echo "kibana is running"
    fi
}
stop() {
    if [ `ps aux|grep elasticsearch | grep -v grep|wc -l` -eq 0 ];then 
        echo "No running program found elasticsearch"
    else
        ps_uid=`ps aux|grep elasticsearch | grep -v grep | awk '{print $2}'`
        kill -9 $ps_uid
        #[ $? -eq 0 ] && rm -f /var/lock/subsys/elasticsearch
        echo "elasticsearch is stop" true
    fi
    if [ `ps aux|grep kibana | grep -v grep|wc -l` -eq 0 ];then 
        echo "No running program found kibana"
    else
        ps_uid=`ps aux|grep kibana | grep -v grep | awk '{print $2}'`
        kill -9 $ps_uid
        #[ $? -eq 0 ] && rm -f /var/lock/subsys/elasticsearch
        echo "kibana is stop" true
    fi
     if [ `ps aux|grep logstash | grep -v grep|wc -l` -eq 0 ];then 
        echo "No running program found logstash"
    else
        ps_uid=`ps aux|grep logstash | grep -v grep | awk '{print $2}'`
        kill -9 $ps_uid
        #[ $? -eq 0 ] && rm -f /var/lock/subsys/elasticsearch
        echo "logstash is stop" true
    fi
}
restart() {
    stop
    start
}
case "$1" in
start)
    start
    ;;
stop)
    stop
    ;;
restart)
    stop
    start
    ;;
*)
    echo $"Use $0 start|stop|restart"
esac
