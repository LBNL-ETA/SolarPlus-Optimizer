# SolarPlus-Optimizer
This repository is for the development of the Solar+ Optimization software.  

## Structure
``models`` contains the modelica models and associated information for MPC and emulation.

``process`` contains scripts to run analyses, MPC optimization, and other control-related algorithms.

``doc`` contains documentation items, such as specifications, reports, and user guide.

``docker`` contains materials to build the necessary Docker images to run the application.

``unittests`` contains testing for software development.

## Build the Docker Image
``$ make build``

## Running an Optimization Process
An optimization process can be run by:

1. ``$ make run`` to start the Docker container and enter its terminal.  Note that the Docker image must be built already (see ``Build the Docker Image`` above).

2. ``$ python process/optimize.py`` to run the control optimization script.

3. ``$ python process/estimate.py`` to run the model parameter estimation script.

## Edits, Enhancements, and New Features
Large edits, enhancements, new features, and bug fixes should be made on separate branches from the master, and merged to the master only after completion. Do this by the following process:

1) Create new issue.
2) Create new branch locally with name issueNo_briefDescription.
3) Make edits, enhancements, new features on new branch locally.
4) Merge latest master to new branch locally and ensure proper operation.
5) Merge branch to master through pull request.
