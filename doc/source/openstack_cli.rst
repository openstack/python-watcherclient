=====================================================================
:program:`openstack` Command-Line Interface (CLI) with Watcher plugin
=====================================================================

.. program:: openstack
.. highlight:: bash

SYNOPSIS
========

:program:`openstack` [options] :program:`optimize` <command> [command-options]

:program:`openstack help optimize`

:program:`openstack help optimize` <command>


DESCRIPTION
===========

The :program:`openstack` command-line interface (CLI) can interact with the
OpenStack infra-optim Service (Watcher), by using our additional plugin
(included into the python-watcherclient package).

In order to use the CLI, you must provide your OpenStack username, password,
project (historically called tenant), and auth endpoint. You can use
configuration options :option:`--os-username`, :option:`--os-password`,
:option:`--os-tenant-id` (or :option:`--os-tenant-name`),
and :option:`--os-auth-url`, or set the corresponding
environment variables::

    $ export OS_USERNAME=user
    $ export OS_PASSWORD=password
    $ export OS_TENANT_ID=b363706f891f48019483f8bd6503c54b   # or OS_TENANT_NAME
    $ export OS_TENANT_NAME=project                          # or OS_TENANT_ID
    $ export OS_AUTH_URL=http://auth.example.com:5000/v2.0

The command-line tool will attempt to reauthenticate using the provided
credentials for every request. You can override this behavior by manually
supplying an auth token using :option:`--watcher-url` and
:option:`--os-auth-token`, or by setting the corresponding environment variables::

    export WATCHER_URL=http://watcher.example.org:9322/
    export OS_AUTH_TOKEN=3bcc3d3a03f44e3d8377f9247b0ad155

Since Keystone can return multiple regions in the Service Catalog, you can
specify the one you want with :option:`--os-region-name` or set the following
environment variable. (It defaults to the first in the list returned.)
::

    $ export OS_REGION_NAME=region

OPTIONS
=======

To get a list of available (sub)commands and options, run::

    $ openstack help optimize

To get usage and options of a command, run::

    $ openstack help optimize <command>


EXAMPLES
========

Get information about the audit-create command::

    $ openstack help optimize audit create


Get a list of available goal::

    $ openstack optimize goal list


Get a list of audits::

    $ openstack optimize audit list

