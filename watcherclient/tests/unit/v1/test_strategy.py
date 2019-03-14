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
import watcherclient.v1.strategy

STRATEGY1 = {
    'uuid': '2cf86250-d309-4b81-818e-1537f3dba6e5',
    'name': 'basic',
    'display_name': 'Basic consolidation',
    'strategy_id': 'SERVER_CONSOLIDATION',
}

STRATEGY2 = {
    'uuid': 'b20bb987-ea8f-457a-a4ea-ab3ffdfeff8b',
    'name': 'dummy',
    'display_name': 'Dummy',
    'strategy_id': 'DUMMY',
}

fake_responses = {
    '/v1/strategies':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY1]},
        ),
    },
    '/v1/strategies/detail':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY1]},
        )
    },
    '/v1/strategies/%s' % STRATEGY1['uuid']:
    {
        'GET': (
            {},
            STRATEGY1,
        ),
    },
    '/v1/strategies/%s' % STRATEGY1['name']:
    {
        'GET': (
            {},
            STRATEGY1,
        ),
    },
    '/v1/strategies/%s/state' % STRATEGY1['name']:
    {
        'GET': (
            {},
            STRATEGY1,
        ),
    },
}

fake_responses_pagination = {
    '/v1/strategies':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY1],
             "next": "http://127.0.0.1:9322/v1/strategies/?limit=1"}
        ),
    },
    '/v1/strategies/?limit=1':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/strategies/?sort_key=id':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY1, STRATEGY2]}
        ),
    },
    '/v1/strategies/?sort_dir=desc':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY2, STRATEGY1]}
        ),
    },
}

fake_responses_marker = {
    '/v1/strategies/?marker=2cf86250-d309-4b81-818e-1537f3dba6e5':
    {
        'GET': (
            {},
            {"strategies": [STRATEGY2]}
        ),
    },
}


class StrategyManagerTest(testtools.TestCase):

    def setUp(self):
        super(StrategyManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)

    def test_strategies_list(self):
        strategies = self.mgr.list()
        expect = [
            ('GET', '/v1/strategies', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(strategies))

    def test_strategies_list_detail(self):
        strategies = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/strategies/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(strategies))

    def test_strategies_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_marker)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(marker=STRATEGY1['uuid'])
        expect = [
            ('GET',
             '/v1/strategies/?marker=2cf86250-d309-4b81-818e-1537f3dba6e5',
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(strategies))

    def test_strategies_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/strategies/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(strategies, matchers.HasLength(1))

    def test_strategies_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/strategies', {}, None),
            ('GET', '/v1/strategies/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(strategies, matchers.HasLength(2))

    def test_strategies_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(sort_key='id')
        expect = [
            ('GET', '/v1/strategies/?sort_key=id', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(strategies))

    def test_strategies_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/strategies/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(strategies))

    def test_strategies_show(self):
        strategy = self.mgr.get(STRATEGY1['uuid'])
        expect = [
            ('GET', '/v1/strategies/%s' % STRATEGY1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(STRATEGY1['uuid'], strategy.uuid)

    def test_strategies_show_by_name(self):
        strategy = self.mgr.get(STRATEGY1['name'])
        expect = [
            ('GET', '/v1/strategies/%s' % STRATEGY1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(STRATEGY1['name'], strategy.name)

    def test_strategies_state(self):
        self.mgr.state(STRATEGY1['name'])
        expect = [
            ('GET', '/v1/strategies/%s/state' % STRATEGY1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
