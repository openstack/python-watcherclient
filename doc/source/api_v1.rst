.. _api_v1:

========================
watcherclient Python API
========================

The watcherclient python API lets you access watcher, the OpenStack
TODEFINE Service.

For example, to manipulate audits, you interact with an `watcherclient.v1.audit`_ object.
You obtain access to audits via attributes of the `watcherclient.v1.client.Client`_ object.

Usage
=====

Get a Client object
-------------------
First, create an `watcherclient.v1.client.Client`_ instance by passing your
credentials to `watcherclient.client.get_client()`_. By default, the
Watcher system is configured so that only administrators (users with 
'admin' role) have access.

There are two different sets of credentials that can be used::

   * watcher endpoint and auth token
   * Identity Service (keystone) credentials

Using watcher endpoint and auth token
.....................................

An auth token and the watcher endpoint can be used to authenticate::

      * os_auth_token: authentication token (from Identity Service)
      * watcher_url: watcher API endpoint, eg http://watcher.example.org:9322/v1

To create the client, you can use the API like so::

   >>> from watcherclient import client
   >>>
   >>> kwargs = {'os_auth_token': '3bcc3d3a03f44e3d8377f9247b0ad155'
   >>>           'watcher_url': 'http://watcher.example.org:9322/'}
   >>> watcher = client.get_client(1, **kwargs)

Using Identity Service (keystone) credentials
.............................................

These Identity Service credentials can be used to authenticate::

   * os_username: name of user
   * os_password: user's password
   * os_auth_url: Identity Service endpoint for authorization
   * os_tenant_{name|id}: name or ID of tenant

To create a client, you can use the API like so::

   >>> from watcherclient import client
   >>>
   >>> kwargs = {'os_username': 'name',
   >>>           'os_password': 'password',
   >>>           'os_auth_url': 'http://keystone.example.org:5000/',
   >>>           'os_tenant_name': 'tenant'}
   >>> watcher = client.get_client(1, **kwargs)

Perform watcher operations
--------------------------

Once you have an watcher `Client`_, you can perform various tasks::

   >>> watcher.action.list()  # list of actions
   >>> watcher.action_plan.list()  # list of action_plan
   >>> watcher.audit.get(audit_uuid)  # information about a particular audit

When the `Client`_ needs to propagate an exception, it will usually
raise an instance subclassed from
`watcherclient.exc.BaseException`_ or `watcherclient.exc.ClientException`_.

Refer to the modules themselves, for more details.

=====================
watcherclient Modules
=====================

.. toctree::
    :maxdepth: 1

    modules <api/autoindex>


.. _watcherclient.v1.audit: api/watcherclient.v1.audit.html#watcherclient.v1.audit.Audit
.. _watcherclient.v1.client.Client: api/watcherclient.v1.client.html#watcherclient.v1.client.Client
.. _Client: api/watcherclient.v1.client.html#watcherclient.v1.client.Client
.. _watcherclient.client.get_client(): api/watcherclient.client.html#watcherclient.client.get_client
.. _watcherclient.exc.BaseException: api/watcherclient.exc.html#watcherclient.exc.BaseException
.. _watcherclient.exc.ClientException: api/watcherclient.exc.html#watcherclient.exc.ClientException
