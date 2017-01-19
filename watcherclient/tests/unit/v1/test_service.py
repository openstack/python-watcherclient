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


import testtools
from testtools import matchers

from watcherclient.tests.unit import utils
import watcherclient.v1.service

SERVICE1 = {
    'id': 1,
    'name': 'watcher-applier',
    'host': 'controller',
    'status': 'ACTIVE',
}

SERVICE2 = {
    'id': 2,
    'name': 'watcher-decision-engine',
    'host': 'controller',
    'status': 'FAILED',
}

fake_responses = {
    '/v1/services':
    {
        'GET': (
            {},
            {"services": [SERVICE1]},
        ),
    },
    '/v1/services/detail':
    {
        'GET': (
            {},
            {"services": [SERVICE1]},
        )
    },
    '/v1/services/%s' % SERVICE1['id']:
    {
        'GET': (
            {},
            SERVICE1,
        ),
    },
    '/v1/services/%s' % SERVICE1['name']:
    {
        'GET': (
            {},
            SERVICE1,
        ),
    },
}

fake_responses_pagination = {
    '/v1/services':
    {
        'GET': (
            {},
            {"services": [SERVICE1],
             "next": "http://127.0.0.1:6385/v1/services/?limit=1"}
        ),
    },
    '/v1/services/?limit=1':
    {
        'GET': (
            {},
            {"services": [SERVICE2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/services/?sort_key=id':
    {
        'GET': (
            {},
            {"services": [SERVICE1, SERVICE2]}
        ),
    },
    '/v1/services/?sort_dir=desc':
    {
        'GET': (
            {},
            {"services": [SERVICE2, SERVICE1]}
        ),
    },
}


class ServiceManagerTest(testtools.TestCase):

    def setUp(self):
        super(ServiceManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.service.ServiceManager(self.api)

    def test_services_list(self):
        services = self.mgr.list()
        expect = [
            ('GET', '/v1/services', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(services))

    def test_services_list_detail(self):
        services = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/services/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(services))

    def test_services_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.service.ServiceManager(self.api)
        services = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/services/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(services, matchers.HasLength(1))

    def test_services_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.service.ServiceManager(self.api)
        services = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/services', {}, None),
            ('GET', '/v1/services/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(services, matchers.HasLength(2))

    def test_services_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.service.ServiceManager(self.api)
        services = self.mgr.list(sort_key='id')
        expect = [
            ('GET', '/v1/services/?sort_key=id', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(services))

    def test_services_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.service.ServiceManager(self.api)
        services = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/services/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(services))

    def test_services_show(self):
        service = self.mgr.get(SERVICE1['id'])
        expect = [
            ('GET', '/v1/services/%s' % SERVICE1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SERVICE1['id'], service.id)

    def test_services_show_by_name(self):
        service = self.mgr.get(SERVICE1['name'])
        expect = [
            ('GET', '/v1/services/%s' % SERVICE1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SERVICE1['name'], service.name)
