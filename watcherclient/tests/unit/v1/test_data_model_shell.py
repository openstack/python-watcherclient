# Copyright 2019 ZTE Corporation.
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
import mock
import six

from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields


DATA_MODEL = {
    'context': [{
        "server_uuid": "1bf91464-9b41-428d-a11e-af691e5563bb",
        "server_name": "fake-name",
        "server_state": "active",
        "server_vcpus": "1",
        "server_memory": "512",
        "server_disk": "1",
        "node_uuid": "253e5dd0-9384-41ab-af13-4f2c2ce26112",
        "node_hostname": "localhost.localdomain",
        "node_vcpus": "4",
        "node_vcpu_ratio": "16.0",
        "node_memory": "16383",
        "node_memory_ratio": "1.5",
        "node_disk": "37",
        "node_disk_ratio": "1.0",
        "node_state": "up",
        }]
}

LIST_RESULT = [{
    "Server UUID": "1bf91464-9b41-428d-a11e-af691e5563bb",
    "Server Name": "fake-name",
    "Server Vcpus": "1",
    "Server Memory": "512",
    "Server Disk": "1",
    "Server State": "active",
    "Node UUID": "253e5dd0-9384-41ab-af13-4f2c2ce26112",
    "Node Host Name": "localhost.localdomain",
    "Node Vcpus": "4",
    "Node Vcpu Ratio": "16.0",
    "Node Memory": "16383",
    "Node Memory Ratio": "1.5",
    "Node Disk": "37",
    "Node Disk Ratio": "1.0",
    "Node State": "up",
}]

SHORT_LIST_RESULT = [{
    "Server UUID": "1bf91464-9b41-428d-a11e-af691e5563bb",
    "Server Name": "fake-name",
    "Server State": "active",
    "Node UUID": "253e5dd0-9384-41ab-af13-4f2c2ce26112",
    "Node Host Name": "localhost.localdomain",
}]


class DataModelShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.COMPUTE_MODEL_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.COMPUTE_MODEL_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.COMPUTE_MODEL_LIST_FIELDS
    FIELD_LABELS = resource_fields.COMPUTE_MODEL_LIST_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_data_model_manager = mock.patch.object(
            resource, 'DataModelManager')

        self.m_data_model_mgr_cls = p_data_model_manager.start()

        self.addCleanup(p_data_model_manager.stop)

        self.m_data_model_mgr = mock.Mock()

        self.m_data_model_mgr_cls.return_value = self.m_data_model_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_data_model_list(self):
        data_model = resource.DataModel(mock.Mock(), DATA_MODEL)
        self.m_data_model_mgr.list.return_value = data_model

        exit_code, results = self.run_cmd('datamodel list')

        self.assertEqual(0, exit_code)
        expect_values = sorted(SHORT_LIST_RESULT[0].values())
        result_values = sorted(results[0].values())
        self.assertEqual(expect_values, result_values)

    def test_do_data_model_list_detail(self):
        data_model = resource.DataModel(mock.Mock(), DATA_MODEL)
        self.m_data_model_mgr.list.return_value = data_model

        exit_code, results = self.run_cmd('datamodel list --detail')

        self.assertEqual(0, exit_code)
        expect_values = sorted(LIST_RESULT[0].values())
        result_values = sorted(results[0].values())
        self.assertEqual(expect_values, result_values)

    def test_do_data_model_list_filter_by_audit(self):
        data_model = resource.DataModel(mock.Mock(), DATA_MODEL)
        self.m_data_model_mgr.list.return_value = data_model

        exit_code, results = self.run_cmd(
            'datamodel list --audit '
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588')

        self.assertEqual(0, exit_code)
        expect_values = sorted(SHORT_LIST_RESULT[0].values())
        result_values = sorted(results[0].values())
        self.assertEqual(expect_values, result_values)
