..
      Except where otherwise noted, this document is licensed under Creative
      Commons Attribution 3.0 License.  You can view the license at:

          https://creativecommons.org/licenses/by/3.0/

=======
Testing
=======

.. _functional_tests:

Functional tests
================

The following procedure gets you started with Tempest testing but you can also
refer to the `Tempest documentation`_ for more details.

.. _Tempest documentation: http://docs.openstack.org/developer/tempest/


Tempest installation
--------------------

You need to install virtualenv, create a virtual environment and activate it::

    $ pip install virtualenv
    $ virtualenv watcher-env
    $ source watcher-env/bin/activate

Then, to install Tempest you can issue the following commands::

    $ git clone https://github.com/openstack/tempest/
    $ pip install tempest/

There should be set environment variables using the OpenStack RC file. If
you don't have RC file yet, create ``admin-openrc`` file and fill it using
the following example::

    export OS_PROJECT_DOMAIN_NAME=default
    export OS_USER_DOMAIN_NAME=default
    export OS_PROJECT_NAME=admin
    export OS_USERNAME=admin
    export OS_PASSWORD=admin
    export OS_AUTH_URL=http://controller:35357/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2

Then, save file and execute ``source admin-openrc`` to set environment
variables.

To run functional tests you need to go to python-watcherclient folder, install
all requirements and execute ``tempest run`` command::

    $ pip install -r requirements.txt test-requirements.txt
    $ pip install .
    $ tempest run --regex watcherclient.tests.functional

You can run specified test(s) by using regular expression::

    $ tempest run --regex watcherclient.tests.functional.v1.test_action.ActionTests.test_action_list
