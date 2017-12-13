# Copyright 2013 Red Hat, Inc.
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

import copy

import testtools
from testtools import matchers

from watcherclient.tests.unit import utils
import watcherclient.v1.audit


AUDIT1 = {
    'id': 1,
    'uuid': '5869da81-4876-4687-a1ed-12cd64cf53d9',
    'audit_type': 'ONE_SHOT',
    'goal': 'fc087747-61be-4aad-8126-b701731ae836',
    'strategy': '2cf86250-d309-4b81-818e-1537f3dba6e5',
}

AUDIT2 = {
    'id': 2,
    'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'audit_type': 'ONE_SHOT',
    'goal': 'fc087747-61be-4aad-8126-b701731ae836',
    'strategy': None,
}


CREATE_AUDIT = copy.deepcopy(AUDIT1)
del CREATE_AUDIT['id']
del CREATE_AUDIT['uuid']

UPDATED_AUDIT1 = copy.deepcopy(AUDIT1)
NEW_STATE = 'SUCCESS'
UPDATED_AUDIT1['state'] = NEW_STATE

fake_responses = {
    '/v1/audits':
    {
        'GET': (
            {},
            {"audits": [AUDIT1]},
        ),
        'POST': (
            {},
            CREATE_AUDIT,
        ),
    },
    '/v1/audits/detail':
    {
        'GET': (
            {},
            {"audits": [AUDIT1]},
        ),
    },
    '/v1/audits/%s' % AUDIT1['uuid']:
    {
        'GET': (
            {},
            AUDIT1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_AUDIT1,
        ),
    },
    '/v1/audits/detail?uuid=%s' % AUDIT1['uuid']:
    {
        'GET': (
            {},
            {"audits": [AUDIT1]},
        ),
    },
}

fake_responses_pagination = {
    '/v1/audits':
    {
        'GET': (
            {},
            {"audits": [AUDIT1],
             "next": "http://127.0.0.1:9322/v1/audits/?limit=1"}
        ),
    },
    '/v1/audits/?limit=1':
    {
        'GET': (
            {},
            {"audits": [AUDIT2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/audits/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"audits": [AUDIT2, AUDIT1]}
        ),
    },
    '/v1/audits/?sort_dir=desc':
    {
        'GET': (
            {},
            {"audits": [AUDIT2, AUDIT1]}
        ),
    },
}

fake_responses_goal = {
    '/v1/audits/?goal=dummy':
    {
        'GET': (
            {},
            {"audits": [AUDIT2, AUDIT1]}
        ),
    },
}

fake_responses_strategy = {
    '/v1/audits/?strategy=dummy':
    {
        'GET': (
            {},
            {"audits": [AUDIT1]}
        ),
    },
}

fake_responses_marker = {
    '/v1/audits/?marker=5869da81-4876-4687-a1ed-12cd64cf53d9':
    {
        'GET': (
            {},
            {"audits": [AUDIT2]}
        ),
    },
}


class AuditManagerTest(testtools.TestCase):
    def setUp(self):
        super(AuditManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)

    def test_audits_list(self):
        audits = self.mgr.list()
        expect = [
            ('GET', '/v1/audits', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audits))

    def test_audits_list_detail(self):
        audits = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/audits/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audits))

    def test_audits_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/audits/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(audits, matchers.HasLength(1))

    def test_audits_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/audits', {}, None),
            ('GET', '/v1/audits/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(audits, matchers.HasLength(2))

    def test_audits_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/audits/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(audits))

    def test_audits_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/audits/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(audits))

    def test_audits_list_goal(self):
        self.api = utils.FakeAPI(fake_responses_goal)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(goal='dummy')
        expect = [
            ('GET', '/v1/audits/?goal=dummy', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(audits))

    def test_audits_list_strategy(self):
        self.api = utils.FakeAPI(fake_responses_strategy)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(strategy='dummy')
        expect = [
            ('GET', '/v1/audits/?strategy=dummy', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audits))

    def test_audits_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_marker)
        self.mgr = watcherclient.v1.audit.AuditManager(self.api)
        audits = self.mgr.list(marker=AUDIT1['uuid'])
        expect = [
            ('GET', '/v1/audits/?marker=5869da81-4876-4687-a1ed-12cd64cf53d9',
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audits))

    def test_audits_show(self):
        audit = self.mgr.get(AUDIT1['uuid'])
        expect = [
            ('GET', '/v1/audits/%s' % AUDIT1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(AUDIT1['uuid'], audit.uuid)

    def test_create(self):
        audit = self.mgr.create(**CREATE_AUDIT)
        expect = [
            ('POST', '/v1/audits', {}, CREATE_AUDIT),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(audit)
