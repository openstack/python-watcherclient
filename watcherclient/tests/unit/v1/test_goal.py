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
import watcherclient.v1.goal

GOAL1 = {
    'uuid': "fc087747-61be-4aad-8126-b701731ae836",
    'name': "SERVER_CONSOLIDATION",
    'display_name': 'Server Consolidation'
}

GOAL2 = {
    'uuid': "407b03b1-63c6-49b2-adaf-4df5c0090047",
    'name': "COST_OPTIMIZATION",
    'display_name': 'Cost Optimization'
}

fake_responses = {
    '/v1/goals':
    {
        'GET': (
            {},
            {"goals": [GOAL1]},
        ),
    },
    '/v1/goals/detail':
    {
        'GET': (
            {},
            {"goals": [GOAL1]},
        )
    },
    '/v1/goals/%s' % GOAL1['uuid']:
    {
        'GET': (
            {},
            GOAL1,
        ),
    },
    '/v1/goals/%s' % GOAL1['name']:
    {
        'GET': (
            {},
            GOAL1,
        ),
    },
}

fake_responses_pagination = {
    '/v1/goals':
    {
        'GET': (
            {},
            {"goals": [GOAL1],
             "next": "http://127.0.0.1:9322/v1/goals/?limit=1"}
        ),
    },
    '/v1/goals/?limit=1':
    {
        'GET': (
            {},
            {"goals": [GOAL2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/goals/?sort_key=id':
    {
        'GET': (
            {},
            {"goals": [GOAL1, GOAL2]}
        ),
    },
    '/v1/goals/?sort_dir=desc':
    {
        'GET': (
            {},
            {"goals": [GOAL2, GOAL1]}
        ),
    },
}

fake_responses_marker = {
    '/v1/goals/?marker=fc087747-61be-4aad-8126-b701731ae836':
    {
        'GET': (
            {},
            {"goals": [GOAL2]}
        ),
    },
}


class GoalManagerTest(testtools.TestCase):

    def setUp(self):
        super(GoalManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.goal.GoalManager(self.api)

    def test_goals_list(self):
        goals = self.mgr.list()
        expect = [
            ('GET', '/v1/goals', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(goals))

    def test_goals_list_detail(self):
        goals = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/goals/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(goals))

    def test_goals_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.goal.GoalManager(self.api)
        goals = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/goals/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(goals, matchers.HasLength(1))

    def test_goals_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_marker)
        self.mgr = watcherclient.v1.goal.GoalManager(self.api)
        goals = self.mgr.list(marker=GOAL1['uuid'])
        expect = [
            ('GET', '/v1/goals/?marker=fc087747-61be-4aad-8126-b701731ae836',
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(goals))

    def test_goals_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.goal.GoalManager(self.api)
        goals = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/goals', {}, None),
            ('GET', '/v1/goals/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(goals, matchers.HasLength(2))

    def test_goals_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.goal.GoalManager(self.api)
        goals = self.mgr.list(sort_key='id')
        expect = [
            ('GET', '/v1/goals/?sort_key=id', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(goals))

    def test_goals_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.goal.GoalManager(self.api)
        goals = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/goals/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(goals))

    def test_goals_show(self):
        goal = self.mgr.get(GOAL1['uuid'])
        expect = [
            ('GET', '/v1/goals/%s' % GOAL1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(GOAL1['uuid'], goal.uuid)

    def test_goals_show_by_name(self):
        goal = self.mgr.get(GOAL1['name'])
        expect = [
            ('GET', '/v1/goals/%s' % GOAL1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(GOAL1['name'], goal.name)
