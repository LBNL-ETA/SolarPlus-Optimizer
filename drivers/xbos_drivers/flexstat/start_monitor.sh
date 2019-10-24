# bash start_monitor.sh
cd /home/solarplus/xboswave/python/pyxbos/pyxbos/drivers/flexstat
python flexstat.py flexstat_config.yaml & 
p0=$!
echo "$p0" > /home/solarplus/xboswave/python/pyxbos/pyxbos/drivers/flexstat/pid.txt
now=`date`
echo "$now: started as $p0"

while true; do
	status=true
	while $status; do
		if [ ! -d /proc/$p0  ]
		then
			status=false
			now=`date`
			echo "$now: process no longer running"
		fi
	done
	python run_always.py test_config.yaml & 
	p0=$!
	echo "$p0" > /home/solarplus/xboswave/python/pyxbos/pyxbos/drivers/flexstat/pid.txt
	now=`date`
	echo "$now: restarted as $p0"
done

