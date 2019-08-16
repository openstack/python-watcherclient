# Copyright 2019 ZTE corporation.
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
import testtools

from watcherclient.tests.unit import utils
import watcherclient.v1.data_model

DATA_MODEL = {
    'context': [{
        "server_uuid": "1bf91464-9b41-428d-a11e-af691e5563bb",
        "server_name": "fake-name",
        "server_state": "active",
        "node_uuid": "253e5dd0-9384-41ab-af13-4f2c2ce26112",
        "node_hostname": "localhost.localdomain",
        }]
}

AUDIT = "81332bfc-36f8-444d-99e2-b7285d602528"

fake_responses = {
    '/v1/data_model/?data_model_type=compute':
    {
        'GET': (
            {},
            DATA_MODEL,
        ),
    },
    '/v1/data_model/?audit_uuid=%s&data_model_type=compute' % AUDIT:
    {
        'GET': (
            {},
            DATA_MODEL,
        ),
    },
}


class DataModelManagerTest(testtools.TestCase):

    def setUp(self):
        super(DataModelManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.data_model.DataModelManager(self.api)

    def test_data_model_list(self):
        data_model = self.mgr.list()
        expect = [
            ('GET', '/v1/data_model/?data_model_type=compute', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(data_model.context))

    def test_data_model_list_audit(self):
        data_model = self.mgr.list(
            audit='%s' % AUDIT)
        expect = [
            ('GET', '/v1/data_model/?'
             'audit_uuid=81332bfc-36f8-444d-99e2-b7285d602528'
             '&data_model_type=compute',
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(data_model.context))
