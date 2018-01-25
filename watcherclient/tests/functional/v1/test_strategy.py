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


class StrategyTests(base.TestCase):
    """Functional tests for strategy."""

    dummy_name = 'dummy'
    basic_strategy = 'basic'
    list_fields = ['UUID', 'Name', 'Display name', 'Goal']
    state_fields = ['Datasource', 'Metrics', 'CDM', 'Name']

    def test_strategy_list(self):
        raw_output = self.watcher('strategy list')
        self.assertIn(self.dummy_name, raw_output)
        self.assert_table_structure([raw_output], self.list_fields)

    def test_strategy_detailed_list(self):
        raw_output = self.watcher('strategy list --detail')
        self.assertIn(self.dummy_name, raw_output)
        self.assert_table_structure([raw_output],
                                    self.list_fields + ['Parameters spec'])

    def test_strategy_show(self):
        raw_output = self.watcher('strategy show %s' % self.dummy_name)
        self.assertIn(self.dummy_name, raw_output)
        self.assert_table_structure([raw_output],
                                    self.list_fields + ['Parameters spec'])
        self.assertNotIn('basic', raw_output)

    def test_strategy_state(self):
        raw_output = self.watcher('strategy state %s' % self.basic_strategy)
        self.assertIn(self.basic_strategy, raw_output)
        self.assert_table_structure([raw_output], self.state_fields)
