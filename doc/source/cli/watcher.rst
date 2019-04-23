===============================================
:program:`watcher` Command-Line Interface (CLI)
===============================================

.. program:: watcher
.. highlight:: bash

SYNOPSIS
========

:program:`watcher` [options] <command> [command-options]

:program:`watcher help`

:program:`watcher help` <command>


DESCRIPTION
===========

The :program:`watcher` command-line interface (CLI) interacts with the
OpenStack infra-optim Service (Watcher).

In order to use the CLI, you must provide your OpenStack username, password,
project (historically called tenant), and auth endpoint. You can use
configuration options :option:``--os-username``, :option:``--os-password``,
:option:``--os-tenant-id`` (or :option:``--os-tenant-name``),
and :option:``--os-auth-url``, or set the corresponding
environment variables::

    $ export OS_USERNAME=user
    $ export OS_PASSWORD=password
    $ export OS_TENANT_ID=b363706f891f48019483f8bd6503c54b   # or OS_TENANT_NAME
    $ export OS_TENANT_NAME=project                          # or OS_TENANT_ID
    $ export OS_AUTH_URL=http://auth.example.com:5000/v3/

The command-line tool will attempt to reauthenticate using the provided
credentials for every request. You can override this behavior by manually
supplying an auth token using :option:``--watcher-url`` and
:option:``--os-auth-token``, or by setting the corresponding environment variables::

    $ export WATCHER_URL=http://watcher.example.org:9322/
    $ export OS_AUTH_TOKEN=3bcc3d3a03f44e3d8377f9247b0ad155

Since Keystone can return multiple regions in the Service Catalog, you can
specify the one you want with :option:``--os-region-name`` or set the following
environment variable. (It defaults to the first in the list returned.)
::

    $ export OS_REGION_NAME=region

Watcher CLI supports bash completion. The command-line tool can automatically
fill partially typed commands. To use this feature, source the below file
(available at
https://opendev.org/openstack/python-watcherclient/src/branch/master/tools/watcher.bash_completion)
to your terminal and then bash completion should work::

    $ . watcher.bash_completion

To avoid doing this every time, add this to your ``.bashrc`` or copy the
watcher.bash_completion file to the default bash completion scripts directory
on your linux distribution.

OPTIONS
=======

To get a list of available (sub)commands and options, run::

    $ watcher help

To get usage and options of a command, run::

    $ watcher help <command>


EXAMPLES
========

Get information about the audit-create command::

    $ watcher help audit create

Get a list of available goal::

    $ watcher goal list

Get a list of audits::

    $ watcher audit list
