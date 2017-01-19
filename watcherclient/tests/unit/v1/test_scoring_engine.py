#
# Copyright 2016 Intel
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
import watcherclient.v1.scoring_engine

SE1 = {
    'uuid': '5b558998-57ed-11e6-9ca8-08002722cb22',
    'name': 'se-01',
    'description': 'Some Scoring Engine'
}

SE2 = {
    'uuid': '1f856554-57ee-11e6-ac72-08002722cb22',
    'name': 'se-02',
    'description': 'Some Other Scoring Engine'
}

fake_responses = {
    '/v1/scoring_engines':
    {
        'GET': (
            {},
            {"scoring_engines": [SE1]},
        ),
    },
    '/v1/scoring_engines/detail':
    {
        'GET': (
            {},
            {"scoring_engines": [SE1]},
        )
    },
    '/v1/scoring_engines/%s' % SE1['uuid']:
    {
        'GET': (
            {},
            SE1,
        ),
    },
    '/v1/scoring_engines/%s' % SE1['name']:
    {
        'GET': (
            {},
            SE1,
        ),
    },
}

fake_responses_pagination = {
    '/v1/scoring_engines':
    {
        'GET': (
            {},
            {"scoring_engines": [SE1],
             "next": "http://127.0.0.1:9322/v1/scoring_engines/?limit=1"}
        ),
    },
    '/v1/scoring_engines/?limit=1':
    {
        'GET': (
            {},
            {"scoring_engines": [SE2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/scoring_engines/?sort_key=id':
    {
        'GET': (
            {},
            {"scoring_engines": [SE1, SE2]}
        ),
    },
    '/v1/scoring_engines/?sort_dir=desc':
    {
        'GET': (
            {},
            {"scoring_engines": [SE2, SE1]}
        ),
    },
}


class ScoringEngineManagerTest(testtools.TestCase):

    def setUp(self):
        super(ScoringEngineManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = \
            watcherclient.v1.scoring_engine.ScoringEngineManager(self.api)

    def test_scoring_engines_list(self):
        scoring_engines = self.mgr.list()
        expect = [
            ('GET', '/v1/scoring_engines', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(scoring_engines))

    def test_scoring_engines_list_detail(self):
        scoring_engines = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/scoring_engines/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(scoring_engines))

    def test_scoring_engines_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = \
            watcherclient.v1.scoring_engine.ScoringEngineManager(self.api)
        scoring_engines = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/scoring_engines/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(scoring_engines, matchers.HasLength(1))

    def test_scoring_engines_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = \
            watcherclient.v1.scoring_engine.ScoringEngineManager(self.api)
        scoring_engines = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/scoring_engines', {}, None),
            ('GET', '/v1/scoring_engines/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(scoring_engines, matchers.HasLength(2))

    def test_scoring_engines_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = \
            watcherclient.v1.scoring_engine.ScoringEngineManager(self.api)
        scoring_engines = self.mgr.list(sort_key='id')
        expect = [
            ('GET', '/v1/scoring_engines/?sort_key=id', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(scoring_engines))

    def test_scoring_engines_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = \
            watcherclient.v1.scoring_engine.ScoringEngineManager(self.api)
        scoring_engines = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/scoring_engines/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(scoring_engines))

    def test_scoring_engines_show(self):
        scoring_engine = self.mgr.get(SE1['uuid'])
        expect = [
            ('GET', '/v1/scoring_engines/%s' % SE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SE1['uuid'], scoring_engine.uuid)

    def test_scoring_engines_show_by_name(self):
        scoring_engine = self.mgr.get(SE1['name'])
        expect = [
            ('GET', '/v1/scoring_engines/%s' % SE1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SE1['name'], scoring_engine.name)
