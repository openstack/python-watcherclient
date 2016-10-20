# Copyright (c) 2016 Intel
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

import datetime
import mock
import six

from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

SCORING_ENGINE_1 = {
    'uuid': '5b558998-57ed-11e6-9ca8-08002722cb22',
    'name': 'se-01',
    'description': 'Scoring Engine 0.1',
    'metainfo': '{ "columns": ["cpu", "mem", "pci"] }',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

SCORING_ENGINE_2 = {
    'uuid': '1f856554-57ee-11e6-ac72-08002722cb22',
    'name': 'se-02',
    'description': 'Some other Scoring Engine',
    'metainfo': 'mode=simplified',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}


class ScoringEngineShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.SCORING_ENGINE_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.SCORING_ENGINE_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.SCORING_ENGINE_FIELDS
    FIELD_LABELS = resource_fields.SCORING_ENGINE_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_se_manager = mock.patch.object(
            resource, 'ScoringEngineManager')
        self.m_se_mgr_cls = p_se_manager.start()
        self.addCleanup(p_se_manager.stop)

        self.m_se_mgr = mock.Mock()
        self.m_se_mgr_cls.return_value = self.m_se_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_scoringengine_list(self):
        se1 = resource.ScoringEngine(mock.Mock(), SCORING_ENGINE_1)
        se2 = resource.ScoringEngine(mock.Mock(), SCORING_ENGINE_2)
        self.m_se_mgr.list.return_value = [
            se1, se2]

        exit_code, results = self.run_cmd('scoringengine list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(se1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(se2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_se_mgr.list.assert_called_once_with(detail=False)

    def test_do_scoringengine_list_detail(self):
        se1 = resource.Goal(mock.Mock(), SCORING_ENGINE_1)
        se2 = resource.Goal(mock.Mock(), SCORING_ENGINE_2)
        self.m_se_mgr.list.return_value = [
            se1, se2]

        exit_code, results = self.run_cmd('scoringengine list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(se1, self.FIELDS, self.FIELD_LABELS),
             self.resource_as_dict(se2, self.FIELDS, self.FIELD_LABELS)],
            results)

        self.m_se_mgr.list.assert_called_once_with(detail=True)

    def test_do_scoringengine_show_by_name(self):
        scoringengine = resource.Goal(mock.Mock(), SCORING_ENGINE_1)
        self.m_se_mgr.get.return_value = scoringengine

        exit_code, result = self.run_cmd('scoringengine show se-01')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(scoringengine, self.FIELDS,
                                  self.FIELD_LABELS),
            result)
        self.m_se_mgr.get.assert_called_once_with('se-01')

    def test_do_scoringengine_show_by_uuid(self):
        scoringengine = resource.Goal(mock.Mock(), SCORING_ENGINE_1)
        self.m_se_mgr.get.return_value = scoringengine

        exit_code, result = self.run_cmd(
            'scoringengine show 5b558998-57ed-11e6-9ca8-08002722cb22')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(scoringengine, self.FIELDS,
                                  self.FIELD_LABELS),
            result)
        self.m_se_mgr.get.assert_called_once_with(
            '5b558998-57ed-11e6-9ca8-08002722cb22')
