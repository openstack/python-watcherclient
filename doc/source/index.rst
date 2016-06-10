Python bindings to the OpenStack Watcher API
============================================

This is a client for OpenStack Watcher API. There's :doc:`a Python API
<api_v1>` (the :mod:`watcherclient` modules), and a :doc:`command-line script
<cli>` (installed as :program:`watcher`). Each implements the entire
OpenStack Watcher API.

You'll need credentials for an OpenStack cloud in order to use the watcher client.


Contents:

.. toctree::
   :maxdepth: 1

   readme
   installation
   api_v1
   cli
   openstack_cli
   contributing

Contributing
============

Code is hosted at `git.openstack.org`_. Submit bugs to the Watcher project on
`Launchpad`_. Submit code to the openstack/python-watcherclient project using
`Gerrit`_.

.. _git.openstack.org: https://git.openstack.org/cgit/openstack/python-watcherclient
.. _Launchpad: https://launchpad.net/watcher
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow

Testing
-------

The preferred way to run the unit tests is using ``tox``.

See `Consistent Testing Interface`_ for more details.

.. _Consistent Testing Interface: http://git.openstack.org/cgit/openstack/governance/tree/reference/project-testing-interface.rst
.. _Watcher: https://wiki.openstack.org/wiki/Watcher
