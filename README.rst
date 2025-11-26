============================================================
ur_fabrication_control: ur_fabrication_control
============================================================

.. start-badges

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://github.com/gramaziokohler/ur_fabrication_control/blob/master/LICENSE
    :alt: License MIT

.. image:: https://travis-ci.org/gramaziokohler/ur_fabrication_control.svg?branch=master
    :target: https://travis-ci.org/gramaziokohler/ur_fabrication_control
    :alt: Travis CI

.. end-badges

.. Write project description

**A short description of the project** ...

# Installation

Please follow `these instuctions <index.md>`_ for setting up your environment.


Main features
-------------

* feature
* feature
* more features

**ur_fabrication_control** runs on Python x.x and x.x.

Useful hints
-------------

* after building, don't forget to source the bash file:
::

   catkin_make
   source devel/setup.bash

Use
-------------

ROS:

::

    roslaunch ur_modern_driver urXX_bringup.launch robot_ip:=ROBOT_IP_ADDRESS
    roslaunch urXX_moveit_config ur5_moveit_planning_execution.launch
    roslaunch urXX_moveit_config moveit_rviz.launch config:=true


Documentation
-------------

.. Explain how to access documentation: API, examples, etc.

..
.. optional sections:

Requirements
------------

.. Write requirements instructions here


Installation
------------

**ur_fabrication_control** can be installed from source or using pip (when published to PyPI).


From Source
~~~~~~~~~~~

Clone the repository and install:

::

    git clone https://github.com/augmentedfabricationlab/ur_fabrication_control.git
    cd ur_fabrication_control
    pip install -e .


Dependencies
~~~~~~~~~~~~

This package requires the following main dependencies:

* ``compas>=2.1.0`` - Computational framework for collaboration and research in architecture, engineering, and digital fabrication
* ``compas_robots>=0.4.0`` - COMPAS package for robot modeling
* ``compas_fab>=1.0.2`` - Robotic fabrication package for the COMPAS Framework
* ``numpy>=1.15`` - Numerical computing library
* ``scipy>=1.0`` - Scientific computing library

All dependencies will be automatically installed when you pip install this package.


Contributing
------------

Make sure you setup your local development environment correctly:

* Clone the `ur_fabrication_control <https://github.com/gramaziokohler/ur_fabrication_control>`_ repository.
* Install development dependencies and make the project accessible from Rhino:

::

    pip install -r requirements-dev.txt
    invoke add-to-rhino

**You're ready to start working!**

During development, use tasks on the
command line to ease recurring operations:

* ``invoke clean``: Clean all generated artifacts.
* ``invoke check``: Run various code and documentation style checks.
* ``invoke docs``: Generate documentation.
* ``invoke test``: Run all tests and checks in one swift command.
* ``invoke add-to-rhino``: Make the project accessible from Rhino.
* ``invoke``: Show available tasks.

For more details, check the `Contributor's Guide <CONTRIBUTING.rst>`_.


Releasing this project
----------------------

.. Write releasing instructions here


.. end of optional sections
..

Credits
-------------