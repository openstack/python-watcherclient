# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from watcherclient._i18n import _
from watcherclient.common import httpclient
from watcherclient import exceptions
from watcherclient import v1


class Client(object):
    """Client for the Watcher v1 API.

    :param string endpoint: A user-supplied endpoint URL for the watcher
                            service.
    :param function token: Provides token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, endpoint=None, *args, **kwargs):
        """Initialize a new client for the Watcher v1 API."""
        if kwargs.get('os_infra_optim_api_version'):
            kwargs['api_version_select_state'] = "user"
        else:
            if not endpoint:
                raise exceptions.EndpointException(
                    _("Must provide 'endpoint' if os_infra_optim_api_version "
                      "isn't specified"))

            # If the user didn't specify a version, use a cached version if
            # one has been stored
            host, netport = httpclient.get_server(endpoint)
            kwargs['api_version_select_state'] = "default"
            kwargs['os_infra_optim_api_version'] = httpclient.DEFAULT_VER

        self.http_client = httpclient._construct_http_client(
            endpoint, *args, **kwargs)

        self.audit = v1.AuditManager(self.http_client)
        self.audit_template = v1.AuditTemplateManager(self.http_client)
        self.action = v1.ActionManager(self.http_client)
        self.action_plan = v1.ActionPlanManager(self.http_client)
        self.goal = v1.GoalManager(self.http_client)
        self.scoring_engine = v1.ScoringEngineManager(self.http_client)
        self.service = v1.ServiceManager(self.http_client)
        self.strategy = v1.StrategyManager(self.http_client)
        self.data_model = v1.DataModelManager(self.http_client)
