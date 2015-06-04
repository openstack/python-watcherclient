# -*- coding: utf-8 -*-

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

from six.moves.urllib import parse as urlparse
import testtools
from testtools.matchers import HasLength

from watcherclient.tests import utils
import watcherclient.v1.audit_template

AUDIT_TMPL1 = {
    'id': 1,
    'uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'name': 'Audit Template 1',
    'description': 'Audit Template 1 description',
    'host_aggregate': 5,
    'extra': {'automatic': False},
    'goal': 'MINIMIZE_LICENSING_COST'
}

AUDIT_TMPL2 = {
    'id': 2,
    'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'name': 'Audit Template 2',
    'description': 'Audit Template 2 description',
    'host_aggregate': 8,
    'extra': {'automatic': True},
    'goal': 'SERVERS_CONSOLIDATION'
}

AUDIT_TMPL3 = {
    'id': 3,
    'uuid': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'name': 'Audit Template 3',
    'description': 'Audit Template 3 description',
    'host_aggregate': 7,
    'extra': {'automatic': True},
    'goal': 'MINIMIZE_LICENSING_COST'
}

CREATE_AUDIT_TEMPLATE = copy.deepcopy(AUDIT_TMPL1)
del CREATE_AUDIT_TEMPLATE['id']
del CREATE_AUDIT_TEMPLATE['uuid']

UPDATED_AUDIT_TMPL1 = copy.deepcopy(AUDIT_TMPL1)
NEW_NAME = 'Audit Template_1 new name'
UPDATED_AUDIT_TMPL1['name'] = NEW_NAME

fake_responses = {
    '/v1/audit_templates':
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1]},
        ),
        'POST': (
            {},
            CREATE_AUDIT_TEMPLATE,
        ),
    },
    '/v1/audit_templates/detail':
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1]},
        ),
    },
    '/v1/audit_templates/%s' % AUDIT_TMPL1['uuid']:
    {
        'GET': (
            {},
            AUDIT_TMPL1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_AUDIT_TMPL1,
        ),
    },
    urlparse.quote('/v1/audit_templates/%s' % AUDIT_TMPL1['name']):
    {
        'GET': (
            {},
            AUDIT_TMPL1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_AUDIT_TMPL1,
        ),
    },
    '/v1/audit_templates/detail?name=%s' % AUDIT_TMPL1['name']:
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1]},
        ),
    },
    '/v1/audit_templates/?name=%s' % AUDIT_TMPL1['name']:
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1]},
        ),
    },
    '/v1/audit_templates/detail?goal=%s' % AUDIT_TMPL1['goal']:
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1, AUDIT_TMPL3]},
        ),
    },
    '/v1/audit_templates/?goal=%s' % AUDIT_TMPL1['goal']:
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1, AUDIT_TMPL3]},
        ),
    }
}

fake_responses_pagination = {
    '/v1/audit_templates':
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL1],
             "next": "http://127.0.0.1:6385/v1/audit_templates/?limit=1"}
        ),
    },
    '/v1/audit_templates/?limit=1':
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/audit_templates/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL3, AUDIT_TMPL2, AUDIT_TMPL1]}
        ),
    },
    '/v1/audit_templates/?sort_dir=desc':
    {
        'GET': (
            {},
            {"audit_templates": [AUDIT_TMPL3, AUDIT_TMPL2, AUDIT_TMPL1]}
        ),
    },
}


class AuditTemplateManagerTest(testtools.TestCase):

    def setUp(self):
        super(AuditTemplateManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.audit_template.AuditTemplateManager(
            self.api)

    def test_audit_templates_list(self):
        audit_templates = self.mgr.list()
        expect = [
            ('GET', '/v1/audit_templates', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audit_templates))

    def test_audit_templates_list_by_name(self):
        audit_templates = self.mgr.list(name=AUDIT_TMPL1['name'])
        expect = [
            ('GET', '/v1/audit_templates/?name=%s' % AUDIT_TMPL1['name'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audit_templates))

    def test_audit_templates_list_detail(self):
        audit_templates = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/audit_templates/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audit_templates))

    def test_audit_templates_list_by_name_detail(self):
        audit_templates = self.mgr.list(name=AUDIT_TMPL1['name'], detail=True)
        expect = [
            ('GET',
             '/v1/audit_templates/detail?name=%s' % AUDIT_TMPL1['name'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(audit_templates))

    def test_audit_templates_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.audit_template.AuditTemplateManager(
            self.api)
        audit_templates = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/audit_templates/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(audit_templates, HasLength(1))

    def test_audit_templates_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.audit_template.AuditTemplateManager(
            self.api)
        audit_templates = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/audit_templates', {}, None),
            ('GET', '/v1/audit_templates/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(audit_templates, HasLength(2))

    def test_audit_templates_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.audit_template.AuditTemplateManager(
            self.api)
        audit_templates = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/audit_templates/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(3, len(audit_templates))

    def test_audit_templates_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.audit_template.AuditTemplateManager(
            self.api)
        audit_templates = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/audit_templates/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(3, len(audit_templates))

    def test_audit_templates_show(self):
        audit_template = self.mgr.get(AUDIT_TMPL1['uuid'])
        expect = [
            ('GET', '/v1/audit_templates/%s' % AUDIT_TMPL1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(AUDIT_TMPL1['uuid'], audit_template.uuid)
        self.assertEqual(AUDIT_TMPL1['name'], audit_template.name)
        self.assertEqual(AUDIT_TMPL1['description'],
                         audit_template.description)
        self.assertEqual(AUDIT_TMPL1['host_aggregate'],
                         audit_template.host_aggregate)
        self.assertEqual(AUDIT_TMPL1['goal'], audit_template.goal)
        self.assertEqual(AUDIT_TMPL1['extra'],
                         audit_template.extra)

    def test_audit_templates_show_by_name(self):
        audit_template = self.mgr.get(urlparse.quote(AUDIT_TMPL1['name']))
        expect = [
            ('GET',
             urlparse.quote('/v1/audit_templates/%s' % AUDIT_TMPL1['name']),
             {}, None),
        ]

        self.assertEqual(expect, self.api.calls)
        self.assertEqual(AUDIT_TMPL1['uuid'], audit_template.uuid)
        self.assertEqual(AUDIT_TMPL1['name'], audit_template.name)
        self.assertEqual(AUDIT_TMPL1['description'],
                         audit_template.description)
        self.assertEqual(AUDIT_TMPL1['host_aggregate'],
                         audit_template.host_aggregate)
        self.assertEqual(AUDIT_TMPL1['goal'], audit_template.goal)
        self.assertEqual(AUDIT_TMPL1['extra'],
                         audit_template.extra)

    def test_create(self):
        audit_template = self.mgr.create(**CREATE_AUDIT_TEMPLATE)
        expect = [
            ('POST', '/v1/audit_templates', {}, CREATE_AUDIT_TEMPLATE),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(audit_template)

    def test_delete(self):
        audit_template = self.mgr.delete(audit_template_id=AUDIT_TMPL1['uuid'])
        expect = [
            ('DELETE',
             '/v1/audit_templates/%s' % AUDIT_TMPL1['uuid'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(audit_template)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        audit_template = self.mgr.update(audit_template_id=AUDIT_TMPL1['uuid'],
                                         patch=patch)
        expect = [
            ('PATCH',
             '/v1/audit_templates/%s' % AUDIT_TMPL1['uuid'],
             {},
             patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, audit_template.name)
