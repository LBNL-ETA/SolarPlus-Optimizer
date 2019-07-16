# RTAC simulator configuration 

## version info for pymodbus:
    use python 3.6.6
    use pymodbus 1.5.2


To test the RTAC driver/XBOS ingester this simulator has been setup to emulate the RTAC with the same register layout.

In order to run the simulator use:
```
python updating_server.py bat_server.yaml
```

The virtual environment modbus_simulator has the necessary versions of Pymodbus and Python to work with the simulator
the port is 5020 by default.
