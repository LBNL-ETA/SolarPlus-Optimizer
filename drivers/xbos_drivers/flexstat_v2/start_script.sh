#! /bin/bash

kill_bg()
{
	pid_to_kill=$1
	echo "killing python process pid=$pid_to_kill"
	kill -9 $pid_to_kill
	process_pid=$$
	echo "killing main script pid=$process_pid"
	kill -9 $$
}

current_id=-1
pid=-1

python flexstat_v2.py flexstat_config_v2.yaml &
pid=$!

while true
do
    sleep 30

    if ps -p $pid > /dev/null
    then
        echo "still running"
    else
        echo "restarting driver"
        python flexstat_v2.py flexstat_config_v2.yaml &
        pid=$!
    fi
done