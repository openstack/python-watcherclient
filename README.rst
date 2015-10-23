===============================
python-watcherclient
===============================

Python client library for Watcher API.

Watcher takes advantage of CEP and ML algorithms/metaheuristics to improve physical resources usage through better VM placement. Watcher can improve your cloud optimization by reducing energy footprint and increasing profits.

* Free software: Apache license
* Wiki: http://wiki.openstack.org/wiki/Watcher
* Source: http://git.openstack.org/cgit/stackforge/python-watcher
* Bugs: http://bugs.launchpad.net/watcher


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

   pip install python-watcherclient


Configuration
=============

Create a **creds** file containing your Openstack credentials:

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

You should be able to launch the following command which gets the list of previously created Audit Templates:

.. code::

   # watcher audit-template-list
   +------+------+
   | UUID | Name |
   +------+------+
   +------+------+

You can view the entire list of available Watcher commands and options using this command:

.. code::

   # watcher help


Troubleshootings
================

If any watcher command fails, you can obtain more details with the **--debug** option :

.. code::

   # watcher --debug audit-template-list

Install the openstack CLI :

.. code::

   # pip install python-openstackclient

Make sure that your Openstack credentials are correct. If so, you should be able to verify that the watcher user has been declared in your Openstack keystone :

.. code::

   # openstack user list

and that the watcher endpoints have been declared as well :

.. code::

   # openstack endpoint list
