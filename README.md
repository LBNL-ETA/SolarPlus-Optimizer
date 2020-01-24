# SolarPlus-Optimizer
This repository is for the development of the Solar+ Optimization software.  

## Structure
``controller`` contains the code that ties together the data acquisition, optimization and sending control signals back.

``models`` contains the modelica models and associated information for MPC and emulation.

``process`` contains scripts to run analyses, MPC optimization, and other control-related algorithms.

``doc`` contains documentation items, such as specifications, reports, and user guide (to be updated).

``simulation`` contains scripts to run simulations for a fixed period using CSV files in data/.

``tests`` contains testing for software development .

## Build the Docker Image
``$ make build``

## Request Data
There are two sources of data:
* static CSV files
* real time data being stored in an influxDB

Please contact [Anand Prakash](mailto:akprakash@lbl.gov) or [Kun Zhang](mailto:kunzhang@lbl.gov) for access to the data.

## Running a Simulation 
A simulation using the modelica models and optimization using MPCPy can be run by:

1. ``$ make run`` to start the Docker container and enter its terminal.  Note that the Docker image must be built already (see ``Build the Docker Image`` above).

2. ``$ python simulation/simulate.py`` to run the simulation script

3. Change these times [here](https://github.com/LBNL-ETA/SolarPlus-Optimizer/blob/master/simulation/simulate.py#L21-L22) to run the simulation for different times. 

## Running in Shadow mode
Running the controller in shadow mode involves starting the MPC controller to retrieve real time data from the InfluxDB database, run the optimization and save the generated setpoints into a CSV file. The controller runs every fifthe minute. 

1. ``$ make run`` to start the Docker container and enter its terminal

2. Rename the ``mpc_shadow_config_template.py`` to ``mpc_config.py`` in the ``controller/`` folder and make necessary changes

3. ``$ python controller/control.py`` to run the controller in shadow mode

## Running the MPC controller

This involves starting the MPC controller to retrieve real time data from the InfluxDB database, run the optimization and send the generated setpoints to the actual devices. It uses XBOS's [wavemq](https://github.com/immesys/wavemq) message bus to publish the new setpoints.

1. ``$ make run`` to start the Docker container and enter its terminal.  Note that the Docker image must be built already (see ``Build the Docker Image`` above).

2. Rename the ``mpc_control_config_template.py`` to ``mpc_config.py`` in the ``controller/`` folder and make necessary changes to configure the XBOS setup (there are placeholders in the template)

3. Copy the generated [``pyxbos/``](https://github.com/gtfierro/xboswave/tree/master/python/pyxbos/pyxbos) folder from [xboswave](github.com/gtfierro/xboswave) repository to the main directory

4. ``$ python controller/control.py`` to run the controller

## Edits, Enhancements, and New Features
Large edits, enhancements, new features, and bug fixes should be made on separate branches from the master, and merged to the master only after completion. Do this by the following process:

1) Create new issue.
2) Create new branch locally with name issueNo_briefDescription.
3) Make edits, enhancements, new features on new branch locally.
4) Merge latest master to new branch locally and ensure proper operation.
5) Merge branch to master through pull request.
