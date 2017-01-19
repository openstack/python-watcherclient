# -*- encoding: utf-8 -*-
# Copyright (c) 2016 Servionica
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from watcherclient.tests.functional.v1 import base


class ServiceTests(base.TestCase):
    """Functional tests for service."""

    decision_engine_name = 'watcher-decision-engine'
    applier_name = 'watcher-applier'
    list_fields = ['ID', 'Name', 'Host', 'Status']

    def test_service_list(self):
        raw_output = self.watcher('service list')
        self.assertIn(self.decision_engine_name, raw_output)
        self.assertIn(self.applier_name, raw_output)
        self.assert_table_structure([raw_output], self.list_fields)

    def test_service_detailed_list(self):
        raw_output = self.watcher('service list --detail')
        self.assertIn(self.decision_engine_name, raw_output)
        self.assertIn(self.applier_name, raw_output)
        self.assert_table_structure([raw_output],
                                    self.list_fields + ['Last seen up'])

    def test_service_show(self):
        raw_output = self.watcher('service show %s'
                                  % self.decision_engine_name)
        self.assertIn(self.decision_engine_name, raw_output)
        self.assert_table_structure([raw_output],
                                    self.list_fields + ['Last seen up'])
        self.assertNotIn(self.applier_name, raw_output)
