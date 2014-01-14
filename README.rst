===================================
Presentation of the Shinken project
===================================

Welcome to the Shinken project.

Shinken is a modern, Nagios compatible monitoring tool, written in
Python. Its main goal is to give users a flexible architecture for
their monitoring system that is designed to scale to large environments.
It’s as simple as the “cloud computing” marketing slides, but here,
it’s real!

Shinken is backwards-compatible with the Nagios configuration standard
and plug-ins. It works on any operating system and architecture that
supports Python, which includes Windows and GNU/Linux.

Requirements
============

There are mandatory and conditional requirements for the installation
methods which are described below. Keep in mind that you if use an alternate installation method 
(setup.py or simple extraction to a folder), you have to use
that method as well when you update or remove your installation.

The recommended installation method is the "install script" which tries to
do all the necessary steps for you. Use it if your OS is
compatible with it. 

You can skip/skim over the requirements section and come back to it later
if using the installation script. However, it is recommended to check any 
requirement manually to confirm they are installed correctly.


Mandatory Requirements
----------------------

`shinken` requires

* `Python`__ 2.6 or higher (2.7 will get higher performances)
* `pycurl`__ Python package for Shinken daemon communications
* `setuptools`__ or `distribute` Python package for installation (see below)
* `pymongo`__ Python Package >= 2.1 for the Shinken WebUI


__ http://www.python.org/download/
__ http://pycurl.sourceforge.net/
__ http://pypi.python.org/pypi/setuptools/
__ http://pypi.python.org/pypi/pymongo/



Conditional Requirements
------------------------

If you plan to use the `livestatus` module or the web interface, you will also
need the following Python packages.

* `simplejson`__ only if python 2.5 used
* `ujson`__  (ujson is used in Livestatus for added speed)
* `pysqlite`__
* `kombu`__ required by the Canopsis hypervisor and reporting module
* `python-ldap`__ for active directory authentication (needed by Shinken WebUI ActiveDir_UI module)

* `Python`__ 2.7 is required for developers to run the test suite, shinken/test/

__ http://pypi.python.org/pypi/simplejson/
__ http://pypi.python.org/pypi/ujson/
__ http://code.google.com/p/pysqlite/
__ http://pypi.python.org/pypi/kombu/2.4.5
__ http://pypi.python.org/pypi/python-ldap/
__ http://www.python.org/download/

Installing/Checking Common Requirements on Windows
==================================================

There is an installation guide for Windows and an installation package.

* `Windows Installation guide on the Wiki`__

__ http://www.shinken-monitoring.org/wiki/shinken_10min_start

Installing/Checking Common Requirements on Linux
================================================

Python
------
For Python itself, the version which comes with almost all distributions
should be okay.


How to install Shinken
======================

You can use the install script utility located at the root of the shinken sources.
The script creates the user and group, installs all dependencies, and installs shinken. It is compatible with Debian, Ubuntu, and Centos/Redhat 5.x and 6.x
The only requirement is an internet connection for the server on which you want to install shinken. It also allows you to modify the installation folder in a configuration file.

If you want shinken installed in seconds (default in /usr/local/shinken) ::

1 - `Download`__ and extract the Shinken archive

__ http://www.shinken-monitoring.org/download/

2 - cd into the resulting folder

3 - run the installation script with the -i (install shinken) option

  ./install -i

See the install.d/README file for further information on installing plugins and web frontends.

Typical minimum installation using check scripts defined in Shinken, Shinken WebUI and PNP4Nagios for metrics.
ie. ./install -i && ./install -p nagios-plugins && ./install -p check_mem && ./install -p manubulon && ./install -a pnp4nagios

Update
------
1 - grab the latest shinken archive and extract its content

2 - cd into the resulting folder

3 - backup shinken configuration plugins and addons and copy the backup id::

  ./install -b

4 - remove shinken (if you installed addons with the installer say no to the question about removing the addons)::

  ./install -u

5 - install the new version::

  ./install -i

6 - restore the backup::

  ./install -r backupid


Remove
-------
cd into shinken source folder and run::
  ./install -u

Running
-------
The install script also installs some `init.d` scripts, enables them at boot time and starts them right after the install process ends.



Where is the configuration?
===========================

The configuration is where you put the etc directory, `/etc/shinken` (in
`/usr/local/shinken/etc` for the quick and dirty method, `/etc/shinken`
for the first two methods).

The `nagios.cfg` file is meant to be shared with Nagios. All Shinken
specific objects (like links to daemons or realms) are in the file
`shinken-specific.cfg`.


Do I need to change my existing Nagios configuration?
=====================================================

No, there is no need to change the existing configuration - unless
you want to add some new hosts and services. Once you are comfortable
with Shinken you can start to use its unique and powerful features.


Learn more about how to use and configure Shinken
=================================================

Jump to the `Shinken documentation wiki`__.

__ http://www.shinken-monitoring.org/wiki/


If you find a bug
================================

Bugs are tracked in the `issue list on GitHub`__ . Always search for existing issues before filing a new one (use the search field at the top of the page).
When filing a new bug, please remember to include:

*	A helpful title - use descriptive keywords in the title and body so others can find your bug (avoiding duplicates).
*	Steps to reproduce the problem, with actual vs. expected results
*	Shinken version (or if you're pulling directly from the Git repo, your current commit SHA - use git rev-parse HEAD)
*	OS version
*	If the problem happens with specific code, link to test files (gist.github.com is a great place to upload code).
*	Screenshots are very helpful if you're seeing an error message or a UI display problem. (Just drag an image into the issue description field to include it).

__ http://github.com/naparuba/shinken/issues/
