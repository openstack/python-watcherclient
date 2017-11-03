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
import watcherclient.v1.action

ACTION1 = {
    'id': 1,
    'uuid': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'action_plan': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'description': 'Action_1 description',
    'next': '239f02a5-9649-4e14-9d33-ac2bf67cb755',
    'state': 'PENDING',
}

ACTION2 = {
    'id': 2,
    'uuid': '239f02a5-9649-4e14-9d33-ac2bf67cb755',
    'action_plan': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'description': 'Action_2 description',
    'next': '67653274-eb24-c7ba-70f6-a84e73d80843',
    'state': 'PENDING',
}

ACTION3 = {
    'id': 3,
    'uuid': '67653274-eb24-c7ba-70f6-a84e73d80843',
    'action_plan': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'description': 'Action_3 description',
    'next': None,
    'state': 'PENDING',
}

ACTION_PLAN1 = {
    'id': 1,
    'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'audit': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'state': 'RECOMMENDED'
}

fake_responses = {
    '/v1/actions':
    {
        'GET': (
            {},
            {"actions": [ACTION1, ACTION2, ACTION3]},
        ),
    },
    '/v1/actions/?action_plan_uuid=%s' % ACTION1['action_plan']:
    {
        'GET': (
            {},
            {"actions": [ACTION1, ACTION2]},
        ),
    },
    '/v1/actions/?audit_uuid=%s' % ACTION_PLAN1['audit']:
    {
        'GET': (
            {},
            {"actions": [ACTION3]},
        ),
    },
    '/v1/actions/detail':
    {
        'GET': (
            {},
            {"actions": [ACTION1, ACTION2, ACTION3]},
        ),
    },
    '/v1/actions/%s' % ACTION1['uuid']:
    {
        'GET': (
            {},
            ACTION1,
        ),
        'DELETE': (
            {},
            None,
        ),
    },
    '/v1/actions/detail?action_plan_uuid=%s' % ACTION1['action_plan']:
    {
        'GET': (
            {},
            {"actions": [ACTION1, ACTION2]},
        ),
    },
    '/v1/actions/detail?audit_uuid=%s' % ACTION_PLAN1['audit']:
    {
        'GET': (
            {},
            {"actions": [ACTION3]},
        ),
    }
}

fake_responses_pagination = {
    '/v1/actions':
    {
        'GET': (
            {},
            {"actions": [ACTION1],
             "next": "http://127.0.0.1:9322/v1/actions/?limit=1"}
        ),
    },
    '/v1/actions/?limit=1':
    {
        'GET': (
            {},
            {"actions": [ACTION2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/actions/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"actions": [ACTION3, ACTION2, ACTION1]}
        ),
    },
    '/v1/actions/?sort_dir=desc':
    {
        'GET': (
            {},
            {"actions": [ACTION3, ACTION2, ACTION1]}
        ),
    },
}

fake_responses_marker = {
    '/v1/actions/?marker=770ef053-ecb3-48b0-85b5-d55a2dbc6588':
    {
        'GET': (
            {},
            {"actions": [ACTION2, ACTION3]}
        ),
    },
}


class ActionManagerTest(testtools.TestCase):

    def setUp(self):
        super(ActionManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.action.ActionManager(self.api)

    def test_actions_list(self):
        actions = self.mgr.list()
        expect = [
            ('GET', '/v1/actions', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(3, len(actions))

    def test_actions_list_by_action_plan(self):
        actions = self.mgr.list(action_plan=ACTION1['action_plan'])
        expect = [
            ('GET',
             '/v1/actions/?action_plan_uuid=%s' % ACTION1['action_plan'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(actions))

    def test_actions_list_detail(self):
        actions = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/actions/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(3, len(actions))

    def test_actions_list_by_action_plan_detail(self):
        actions = self.mgr.list(action_plan=ACTION1['action_plan'],
                                detail=True)
        expect = [
            ('GET',
             '/v1/actions/detail?action_plan_uuid=%s' % ACTION1['action_plan'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(actions))

    def test_actions_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.action.ActionManager(self.api)
        actions = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/actions/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(actions, matchers.HasLength(1))

    def test_actions_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.action.ActionManager(self.api)
        actions = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/actions', {}, None),
            ('GET', '/v1/actions/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(actions, matchers.HasLength(2))

    def test_actions_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.action.ActionManager(self.api)
        actions = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/actions/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(3, len(actions))

    def test_actions_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.action.ActionManager(self.api)
        actions = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/actions/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(3, len(actions))

    def test_actions_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_marker)
        self.mgr = watcherclient.v1.action.ActionManager(self.api)
        actions = self.mgr.list(
            marker='770ef053-ecb3-48b0-85b5-d55a2dbc6588')
        expect = [
            ('GET',
             '/v1/actions/?marker=770ef053-ecb3-48b0-85b5-d55a2dbc6588',
             {},
             None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(actions))

    def test_actions_show(self):
        action = self.mgr.get(ACTION1['uuid'])
        expect = [
            ('GET', '/v1/actions/%s' % ACTION1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(ACTION1['uuid'], action.uuid)
        self.assertEqual(ACTION1['action_plan'], action.action_plan)
        self.assertEqual(ACTION1['next'], action.next)
