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

trap 'kill_bg $pid' SIGINT

while IFS=, read -r id st et is_baseline; do
	t_now=`TZ=US/Pacific date +%s`
	st2="$st PDT"
	et2="$et PDT"

	st_dt=`TZ=UTC date -d "$st2"`
	et_dt=`TZ=UTC date -d "$et2"`
	st_ts=`date -d "$st_dt" +%s`
	et_ts=`date -d "$et_dt" +%s`

	while [[ $st_ts -le $t_now  ]] && [[ $t_now -le $et_ts ]];
	do
		echo "currently running test_id=$id"
		if [[ $current_id -ne $id ]];
		then
			echo "new process"
			if [[ $pid -ne -1 ]];
			then
				echo "killing python process pid=$pid"
				kill -9 $pid
			fi
			python3 battery_driver.py battery_driver_config.yaml &
			pid=$!
			echo "starting new python process pid=$pid" 
			current_id=$id
		fi
		t_now=`TZ=US/Pacific date +%s`
		sleep 30
	done
	echo ''
done < /home/solarplus/Solarplus-Optimizer/controller/test_schedule.csv

if [[ $pid -ne -1 ]];
then
	echo "killing python process pid=$pid"
	kill -9 
fi

python3 battery_driver.py battery_driver_config.yaml 
pid=$!
