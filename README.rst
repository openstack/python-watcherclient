========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/tc/badges/python-watcherclient.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on

====================
python-watcherclient
====================

Client for resource optimization service for OpenStack.

OpenStack Watcher provides a flexible and scalable resource optimization
service for multi-tenant OpenStack-based clouds.
Watcher provides a complete optimization loop-including everything from a
metrics receiver, complex event processor and profiler, optimization processor
and an action plan applier. This provides a robust framework to realize a wide
range of cloud optimization goals, including the reduction of data center
operating costs, increased system performance via intelligent virtual machine
migration, increased energy efficiency and more!

* Free software: Apache license
* Wiki: https://wiki.openstack.org/wiki/Watcher
* Source: https://opendev.org/openstack/python-watcherclient
* Bugs: https://bugs.launchpad.net/watcher

Installation
============

Install the prerequisite packages
---------------------------------

On Ubuntu (tested on 14.04-64)

.. code::

   sudo apt-get install python-dev libssl-dev python-pip git-core libmysqlclient-dev libffi-dev

On Fedora-based distributions e.g., Fedora/RHEL/CentOS/Scientific Linux (tested on CentOS 6.5)

.. code::

   sudo yum install python-virtualenv openssl-devel python-pip git gcc libffi-devel mysql-devel postgresql-devel

On openSUSE-based distributions (SLES 12, openSUSE 13.1, Factory or Tumbleweed)

.. code::

   sudo zypper install gcc git libmysqlclient-devel libopenssl-devel postgresql-devel python-devel python-pip

Install the Watcher client
--------------------------

You can install the Watcher CLI with the following command:

.. code::

   sudo pip install python-watcherclient


You can also use the `OpenStack client <https://docs.openstack.org/python-openstackclient/latest/>`_
with Watcher (our watcher plugin for OpenStack client is included in the
python-watcherclient package). To install it, you have just to run this command:

.. code::

   sudo pip install python-openstackclient

Configuration
=============

Create a **creds** file containing your OpenStack credentials:

.. code::

   export OS_IDENTITY_API_VERSION=3
   export OS_AUTH_URL=http://<your-keystone-server>:5000/v3
   export OS_PROJECT_DOMAIN_ID=default
   export OS_USER_DOMAIN_ID=default
   export OS_USERNAME=admin
   export OS_PASSWORD=<your-password>
   export OS_PROJECT_NAME=<your-project-name>

Source these credentials into your current shell session:

.. code::

   # source creds

You should be able to launch the following command which gets the list of
previously created Audit Templates:

.. code::

   # watcher audittemplate list

or::

   # openstack optimize audittemplate list
   +--------------------------------+------+----------------------+----------+
   | UUID                           | Name | Goal                 | Strategy |
   +--------------------------------+------+----------------------+----------+
   +--------------------------------+------+----------------------+----------+


You can view the entire list of available Watcher commands and options using
this command:

.. code::

   # watcher help

or::

   # openstack help optimize


Troubleshootings
================

If any watcher command fails, you can obtain more details with the **--debug**
option :

.. code::

   # watcher --debug audittemplate list

or::

   # openstack --debug optimize audittemplate list


Install the openstack CLI :

.. code::

   # pip install python-openstackclient

Make sure that your Openstack credentials are correct. If so, you should be able
to verify that the watcher user has been declared in your Openstack keystone :

.. code::

   # openstack user list

and that the watcher endpoints have been declared as well :

.. code::

   # openstack endpoint list
