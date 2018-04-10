# SolarPlus-Optimizer
This repository is for the development of the Solar+ Optimization software.  

## Structure
``models`` contains the modelica models and associated information for MPC and emulation.

``process`` contains scripts to run analyses, MPC optimization, and other control-related algorithms.

``doc`` contains documentation items, such as specifications, reports, and user guide.

``docker`` contains materials to build the necessary Docker images to run the application.

``unittests`` contains testing for software development.

## Running an Optimization Process
An optimization process can be run by:

1. ``$ make run`` to start the Docker container and enter its terminal.  Note that the Docker images must be obtained or built already (see ``docker`` directory for building images from a ``Dockerfile``).

2. ``$ python process/optimize.py`` to run the optimization script.

## Edits, Enhancements, and New Features
Large edits, enhancements, new features, and bug fixes should be made on separate branches from the master, and merged to the master only after completion. Please label the new branch accordingly, as briefDescription.
