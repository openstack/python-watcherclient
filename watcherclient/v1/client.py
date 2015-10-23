# -*- coding: utf-8 -*-
#
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

from watcherclient.common import http
from watcherclient.v1 import action
from watcherclient.v1 import action_plan
from watcherclient.v1 import audit
from watcherclient.v1 import audit_template
from watcherclient.v1 import goal
from watcherclient.v1 import metric_collector


class Client(object):
    """Client for the Watcher v1 API.

    :param string endpoint: A user-supplied endpoint URL for the watcher
                            service.
    :param function token: Provides token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Watcher v1 API."""
        self.http_client = http._construct_http_client(*args, **kwargs)
        self.audit = audit.AuditManager(self.http_client)
        self.audit_template = audit_template.AuditTemplateManager(
            self.http_client)
        self.action = action.ActionManager(self.http_client)
        self.action_plan = action_plan.ActionPlanManager(self.http_client)
        self.goal = goal.GoalManager(self.http_client)
        self.metric_collector = metric_collector.MetricCollectorManager(
            self.http_client
        )
