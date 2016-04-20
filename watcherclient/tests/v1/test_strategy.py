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


import testtools
from testtools.matchers import HasLength

from watcherclient.tests import utils
import watcherclient.v1.strategy

STRATEGY1 = {
    'id': "basic",
    'display_name': 'Basic consolidation',
    'strategy_id': "SERVER_CONSOLIDATION",
}

STRATEGY2 = {
    'id': "dummy",
    'display_name': 'Dummy',
    'strategy_id': "DUMMY",
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
    '/v1/strategies/%s' % STRATEGY1['id']:
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
             "next": "http://127.0.0.1:6385/v1/strategies/?limit=1"}
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

    def test_strategies_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/strategies/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(strategies, HasLength(1))

    def test_strategies_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.strategy.StrategyManager(self.api)
        strategies = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/strategies', {}, None),
            ('GET', '/v1/strategies/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(strategies, HasLength(2))

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
        strategy = self.mgr.get(STRATEGY1['id'])
        expect = [
            ('GET', '/v1/strategies/%s' % STRATEGY1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(STRATEGY1['id'], strategy.id)
