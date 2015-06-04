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

import testtools
from testtools.matchers import HasLength

from watcherclient.tests import utils
import watcherclient.v1.metric_collector

METRIC_COLLECTOR1 = {
    'id': 1,
    'uuid': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'category': 'cat1',
    'endpoint': 'http://metric_collector_1:6446',
}

METRIC_COLLECTOR2 = {
    'id': 2,
    'uuid': '67653274-eb24-c7ba-70f6-a84e73d80843',
    'category': 'cat2',
}

METRIC_COLLECTOR3 = {
    'id': 3,
    'uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'category': 'cat2',
    'endpoint': 'http://metric_collector_3:6446',
}

CREATE_METRIC_COLLECTOR = copy.deepcopy(METRIC_COLLECTOR1)
del CREATE_METRIC_COLLECTOR['id']
del CREATE_METRIC_COLLECTOR['uuid']

UPDATED_METRIC_COLLECTOR1 = copy.deepcopy(METRIC_COLLECTOR1)
NEW_ENDPOINT = 'http://metric_collector_1:6447'
UPDATED_METRIC_COLLECTOR1['endpoint'] = NEW_ENDPOINT

fake_responses = {
    '/v1/metric-collectors':
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR1]},
        ),
        'POST': (
            {},
            CREATE_METRIC_COLLECTOR,
        ),
    },
    '/v1/metric-collectors/?category=%s' % METRIC_COLLECTOR1['category']:
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR1]},
        ),
    },
    '/v1/metric-collectors/?category=%s' % METRIC_COLLECTOR2['category']:
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR2, METRIC_COLLECTOR3]},
        ),
    },
    '/v1/metric-collectors/detail':
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR1]},
        ),
    },
    '/v1/metric-collectors/%s' % METRIC_COLLECTOR1['uuid']:
    {
        'GET': (
            {},
            METRIC_COLLECTOR1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_METRIC_COLLECTOR1,
        ),
    },
    '/v1/metric-collectors/detail?category=%s' % METRIC_COLLECTOR1['category']:
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR1]},
        ),
    },
    '/v1/metric-collectors/detail?category=%s' % METRIC_COLLECTOR2['category']:
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR2, METRIC_COLLECTOR3]},
        ),
    },
}

fake_responses_pagination = {
    '/v1/metric-collectors':
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR1],
             "next": "http://127.0.0.1:6385/v1/metric-collectors/?limit=1"}
        ),
    },
    '/v1/metric-collectors/?limit=1':
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/metric-collectors/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR2, METRIC_COLLECTOR1]}
        ),
    },
    '/v1/metric-collectors/?sort_dir=desc':
    {
        'GET': (
            {},
            {"metric-collectors": [METRIC_COLLECTOR2, METRIC_COLLECTOR1]}
        ),
    },
}


class MetricCollectorManagerTest(testtools.TestCase):

    def setUp(self):
        super(MetricCollectorManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.metric_collector \
                                .MetricCollectorManager(self.api)

    def test_metric_collectors_list(self):
        metric_collectors = self.mgr.list()
        expect = [
            ('GET', '/v1/metric-collectors', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(metric_collectors))

    def test_metric_collectors_list_by_category(self):
        metric_collectors = self.mgr.list(
            category=METRIC_COLLECTOR1['category']
        )
        expect = [
            ('GET',
             '/v1/metric-collectors/?category=%s' %
                METRIC_COLLECTOR1['category'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(metric_collectors))

    def test_metric_collectors_list_by_category_bis(self):
        metric_collectors = self.mgr.list(
            category=METRIC_COLLECTOR2['category']
        )
        expect = [
            ('GET',
             '/v1/metric-collectors/?category=%s' %
                METRIC_COLLECTOR2['category'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(metric_collectors))

    def test_metric_collectors_list_detail(self):
        metric_collectors = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/metric-collectors/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(metric_collectors))

    def test_metric_collectors_list_by_category_detail(self):
        metric_collectors = self.mgr.list(
            category=METRIC_COLLECTOR1['category'],
            detail=True)
        expect = [
            ('GET',
             '/v1/metric-collectors/detail?category=%s' %
                METRIC_COLLECTOR1['category'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(metric_collectors))

    def test_metric_collectors_list_by_category_detail_bis(self):
        metric_collectors = self.mgr.list(
            category=METRIC_COLLECTOR2['category'],
            detail=True)
        expect = [
            ('GET',
             '/v1/metric-collectors/detail?category=%s' %
                METRIC_COLLECTOR2['category'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(metric_collectors))

    def test_metric_collectors_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.metric_collector \
                                .MetricCollectorManager(self.api)
        metric_collectors = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/metric-collectors/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(metric_collectors, HasLength(1))

    def test_metric_collectors_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.metric_collector \
                                .MetricCollectorManager(self.api)
        metric_collectors = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/metric-collectors', {}, None),
            ('GET', '/v1/metric-collectors/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(metric_collectors, HasLength(2))

    def test_metric_collectors_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.metric_collector \
                                .MetricCollectorManager(self.api)
        metric_collectors = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/metric-collectors/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(metric_collectors))

    def test_metric_collectors_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.metric_collector \
                                .MetricCollectorManager(self.api)
        metric_collectors = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/metric-collectors/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(metric_collectors))

    def test_metric_collectors_show(self):
        metric_collector = self.mgr.get(METRIC_COLLECTOR1['uuid'])
        expect = [
            ('GET', '/v1/metric-collectors/%s' %
                METRIC_COLLECTOR1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(METRIC_COLLECTOR1['uuid'], metric_collector.uuid)
        self.assertEqual(METRIC_COLLECTOR1['category'],
                         metric_collector.category)
        self.assertEqual(METRIC_COLLECTOR1['endpoint'],
                         metric_collector.endpoint)

    def test_create(self):
        metric_collector = self.mgr.create(**CREATE_METRIC_COLLECTOR)
        expect = [
            ('POST', '/v1/metric-collectors', {}, CREATE_METRIC_COLLECTOR),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(metric_collector)

    def test_delete(self):
        metric_collector = self.mgr.delete(
            metric_collector_id=METRIC_COLLECTOR1['uuid'])
        expect = [
            ('DELETE', '/v1/metric-collectors/%s' %
                METRIC_COLLECTOR1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(metric_collector)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_ENDPOINT,
                 'path': '/endpoint'}
        metric_collector = self.mgr.update(
            metric_collector_id=METRIC_COLLECTOR1['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/metric-collectors/%s' %
                METRIC_COLLECTOR1['uuid'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_ENDPOINT, metric_collector.endpoint)
