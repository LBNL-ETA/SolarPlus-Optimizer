# SolarPlus-Optimizer
This repository is for the development of the Solar+ Optimization software.  

## Structure
``controller`` contains the code that ties together the data acquisition, optimization and sending control signals back.

``models`` contains the Modelica models and associated information for MPC and emulation.

``process`` contains scripts to run data processing, analysis and parameter estimation.

``doc`` contains documentation items, such as specifications, reports, and user guide (to be updated).

``simulation`` contains scripts to run simulations for a fixed period using CSV files in data/.

``tests`` contains testing for the software development.

## Build the Docker Image
``$ make build``

## Request Data
There are two sources of data:
* static CSV files
* real time data being stored in an influxDB

Please contact [Anand Prakash](mailto:akprakash@lbl.gov) or [Kun Zhang](mailto:kunzhang@lbl.gov) for access to the data.

## Running Simulations 
A simulation using the modelica models and optimization using MPCPy can be run by:

1. ``$ make run`` to start the Docker container and enter its terminal.  Note that the Docker image must be built already (see ``Build the Docker Image`` above).

2. ``$ python simulation/simulate.py`` to run the simulation script

3. Change these times [here](https://github.com/LBNL-ETA/SolarPlus-Optimizer/blob/master/simulation/simulate.py#L21-L22) to run the simulation for different times. 

## Running the MPC Controller in Shadow Mode (Open-loop Control)
Running the controller in shadow mode involves starting the MPC controller to retrieve real time data from the InfluxDB database, run the optimization and save the generated setpoints into a CSV file. The controller runs every fifth minute. 

1. ``$ make run`` to start the Docker container and enter its terminal

2. Rename the ``mpc_shadow_config_template.py`` to ``mpc_config.py`` in the ``controller/`` folder and make necessary changes such as changing the tz_computer to your local time zone

3. ``$ python controller/control.py`` to run the controller in shadow mode

## Running the MPC Controller in Realtime (Closed-loop Control)

This involves starting the MPC controller to retrieve real time data from the InfluxDB database, run the optimization and send the generated setpoints to the actual devices. It uses XBOS's [wavemq](https://github.com/immesys/wavemq) message bus to publish the new setpoints.

1. ``$ make run`` to start the Docker container and enter its terminal.  Note that the Docker image must be built already (see ``Build the Docker Image`` above).

2. Rename the ``mpc_control_config_template.py`` to ``mpc_config.py`` in the ``controller/`` folder and make necessary changes to configure the XBOS setup (there are placeholders in the template)

3. Copy the generated [``pyxbos/``](https://github.com/gtfierro/xboswave/tree/master/python/pyxbos/pyxbos) folder from [xboswave](github.com/gtfierro/xboswave) repository to the main directory

4. ``$ python controller/control.py`` to run the controller

## Edits, Enhancements, and New Features
Large edits, enhancements, new features, and bug fixes should be made on separate branches from the master, and merged to the master only after completion. Do this by the following process:

1) Create a new issue.
2) Create a new branch locally with name issueNo_briefDescription.
3) Make edits, enhancements, new features on the new branch locally.
4) Merge latest master to the new branch locally and ensure proper operation.
5) Merge branch to master through a pull request.

## Relevant Publications

*  Krishnan Prakash, A.; Zhang, K.; Gupta, P.; Blum, D.; Marshall, M.; Fierro, G.; Alstone, P.; Zoellick, J.; Brown, R.; Pritoni, M. Solar+ Optimizer: A Model Predictive Control Optimization Platform for Grid Responsive Building Microgrids. Energies 2020, 13, 3093. https://doi.org/10.3390/en13123093 
*  Alstone, Peter, Brown, Richard, Zoellick, Jim, Pritoni, Marco, Blum, David, Radecsky, Kristen, Zhang, Kun, Prakash, Anand, and Perez, Pol. Resilient buildings for fire-adapted landscapes: EE and flexible loads integrated with solar and storage microgrids. United States: N. p., 2020. https://www.osti.gov/biblio/1713313
*  Kun Zhang, Anand Prakash, Lazlo Paul, David Blum, Peter Alstone, James Zoellick, Richard Brown, Marco Pritoni, Model predictive control for demand flexibility: Real-world operation of a commercial building with photovoltaic and battery systems, Advances in Applied Energy, Volume 7, 2022, 100099, ISSN 2666-7924, https://doi.org/10.1016/j.adapen.2022.100099.
*  Paul, L., Prakash, A., Zhang, K., Pritoni, M., & Brown, R. (2022). SolarPlus Optimizer: Integrated Control of Solar, Batteries, and Flexible Loads for Small Commercial Buildings. Lawrence Berkeley National Laboratory. Retrieved from https://escholarship.org/uc/item/5zm0d09s 


## Copyright Notice

SolarPlus-Optimizer Copyright (c) 2022, The Regents of the University
of California, through Lawrence Berkeley National Laboratory (subject
to receipt of any required approvals from the U.S. Dept. of Energy).  
All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at
IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative 
works, and perform publicly and display publicly, and to permit others to do so.

## License

SolarPlus-Optimizer is available under the following [license](https://github.com/LBNL-ETA/SolarPlus-Optimizer/blob/main/License.txt).
