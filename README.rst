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
Follow `these instuctions<index.md>`_for setting up your environment.


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

.. Write installation instructions here


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
