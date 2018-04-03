#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pbr.version

from watcherclient import client
from watcherclient.common import api_versioning
from watcherclient import exceptions


__version__ = pbr.version.VersionInfo(
    'python-watcherclient').version_string()

__all__ = ['client', 'exceptions', ]

API_MIN_VERSION = api_versioning.APIVersion("1.0")
# The max version should be the latest version that is supported in the client,
# not necessarily the latest that the server can provide. This is only bumped
# when client supported the max version, and bumped sequentially, otherwise
# the client may break due to server side new version may include some
# backward incompatible change.
API_MAX_VERSION = api_versioning.APIVersion("1.1")
