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
import mock

import testtools
from testtools import matchers

from oslo_utils.uuidutils import generate_uuid
from watcherclient.common.apiclient.exceptions import HTTPClientError
from watcherclient.tests.unit import utils
import watcherclient.v1.action_plan

ACTION_PLAN1 = {
    'id': 1,
    'uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'audit': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'state': 'RECOMMENDED'
}

ACTION_PLAN2 = {
    'id': 2,
    'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'audit': '239f02a5-9649-4e14-9d33-ac2bf67cb755',
    'state': 'RECOMMENDED'
}

UPDATED_ACTION_PLAN = copy.deepcopy(ACTION_PLAN1)
NEW_STATE = 'PENDING'
UPDATED_ACTION_PLAN['state'] = NEW_STATE

START_ACTION_PLAN = copy.deepcopy(ACTION_PLAN1)
START_ACTION_PLAN['state'] = NEW_STATE

ONGOING_ACTION_PLAN = copy.deepcopy(ACTION_PLAN1)
ONGOING_ACTION_PLAN['state'] = 'ONGOING'

CANCELLING_ACTION_PLAN = copy.deepcopy(ACTION_PLAN1)
CANCELLING_ACTION_PLAN['state'] = 'CANCELLING'

CANCELD_ACTION_PLAN = copy.deepcopy(ACTION_PLAN2)
CANCELD_ACTION_PLAN['state'] = 'CANCELLED'

fake_responses = {
    '/v1/action_plans':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN1, ACTION_PLAN2]},
        ),
    },
    '/v1/action_plans/detail':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN1, ACTION_PLAN2]},
        ),
    },
    '/v1/action_plans/%s' % ACTION_PLAN1['uuid']:
    {
        'GET': (
            {},
            ACTION_PLAN1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_ACTION_PLAN,
        ),
    },
    '/v1/action_plans/%s/start' % ACTION_PLAN1['uuid']:
    {
        'POST': (
            {},
            START_ACTION_PLAN,
        ),
    },
    '/v1/action_plans/detail?uuid=%s' % ACTION_PLAN1['uuid']:
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN1]},
        ),
    },
}

fake_responses_pagination = {
    '/v1/action_plans':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN1],
             "next": "http://127.0.0.1:9322/v1/action_plans/?limit=1"}
        ),
    },
    '/v1/action_plans/?limit=1':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN2]}
        ),
    },
    '/v1/action_plans/?marker=f8e47706-efcf-49a4-a5c4-af604eb492f2':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/action_plans/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN2, ACTION_PLAN1]}
        ),
    },
    '/v1/action_plans/?sort_dir=desc':
    {
        'GET': (
            {},
            {"action_plans": [ACTION_PLAN2, ACTION_PLAN1]}
        ),
    },
}

fake_responses_cancel = {
    '/v1/action_plans/%s' % ACTION_PLAN1['uuid']:
    {
        'GET': (
            {},
            [ONGOING_ACTION_PLAN],
        ),
        'PATCH': (
            {},
            CANCELLING_ACTION_PLAN,
        ),
    },
    '/v1/action_plans/%s' % ACTION_PLAN2['uuid']:
    {
        'GET': (
            {},
            [ACTION_PLAN2],
        ),
        'PATCH': (
            {},
            CANCELD_ACTION_PLAN,
        ),
    },
}


class ActionPlanManagerTest(testtools.TestCase):

    def setUp(self):
        super(ActionPlanManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)

    def test_action_plans_list(self):
        action_plans = self.mgr.list()
        expect = [
            ('GET', '/v1/action_plans', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(action_plans))

    def test_action_plans_list_detail(self):
        action_plans = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/action_plans/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(action_plans))

    def test_action_plans_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)
        action_plans = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/action_plans/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(action_plans, matchers.HasLength(1))

    def test_action_plans_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)
        action_plans = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/action_plans', {}, None),
            ('GET', '/v1/action_plans/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(action_plans, matchers.HasLength(2))

    def test_action_plans_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)
        action_plans = self.mgr.list(
            marker='f8e47706-efcf-49a4-a5c4-af604eb492f2')
        expect = [
            ('GET', '/v1/action_plans/?'
             'marker=f8e47706-efcf-49a4-a5c4-af604eb492f2',
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(action_plans, matchers.HasLength(1))

    def test_action_plans_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)
        action_plans = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/action_plans/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(action_plans))

    def test_action_plans_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)
        action_plans = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/action_plans/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(action_plans))

    def test_action_plans_show(self):
        action_plan = self.mgr.get(ACTION_PLAN1['uuid'])
        expect = [
            ('GET', '/v1/action_plans/%s' % ACTION_PLAN1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(ACTION_PLAN1['uuid'], action_plan.uuid)

    def test_action_plans_get_index_error(self):

        # verify this method will return None when meet indexError
        fake_uuid = generate_uuid()
        self.api.json_request = mock.Mock(return_value=('404', []))
        self.assertIsNone(self.mgr.get(fake_uuid))

    def test_action_plans_delete(self):
        # verity that action plan was successfully deleted
        self.api.raw_request = mock.Mock(return_value=('204', []))
        self.assertIsNone(self.mgr.delete(ACTION_PLAN1['uuid']))

        # verity that delete a wrong action plan will raise Exception
        fake_uuid = generate_uuid()
        self.api.raw_request = mock.Mock(
            side_effect=HTTPClientError('404 Not Found'))
        self.assertRaises(HTTPClientError, self.mgr.delete, fake_uuid)

    def test_action_plans_cancel(self):
        # verity that the status of action plan can be converted from
        # 'ONGOING' to 'CANCELLING'
        self.api = utils.FakeAPI(fake_responses_cancel)
        self.mgr = watcherclient.v1.action_plan.ActionPlanManager(self.api)
        patch = {'op': 'replace',
                 'value': 'CANCELLING',
                 'path': '/state'}
        action_plan = self.mgr.cancel(action_plan_id=ACTION_PLAN1['uuid'])
        expect = [
            ('GET', '/v1/action_plans/%s' % ACTION_PLAN1['uuid'], {}, None),
            ('PATCH', '/v1/action_plans/%s' % ACTION_PLAN1['uuid'], {},
             [patch])
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('CANCELLING', action_plan.state)

        # verity that the status of action plan can be converted from
        # 'RECOMMENDED' to 'CANCELLED'
        patch['value'] = 'CANCELLED'
        self.api.calls = []
        action_plan = self.mgr.cancel(action_plan_id=ACTION_PLAN2['uuid'])
        expect = [
            ('GET', '/v1/action_plans/%s' % ACTION_PLAN2['uuid'], {}, None),
            ('PATCH', '/v1/action_plans/%s' % ACTION_PLAN2['uuid'], {},
             [patch])
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('CANCELLED', action_plan.state)

    def test_action_plan_update(self):
        patch = {'op': 'replace',
                 'value': NEW_STATE,
                 'path': '/state'}
        action_plan = self.mgr.update(action_plan_id=ACTION_PLAN1['uuid'],
                                      patch=patch)
        expect = [
            ('PATCH',
             '/v1/action_plans/%s' % ACTION_PLAN1['uuid'],
             {},
             patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_STATE, action_plan.state)

    def test_action_plan_start(self):
        action_plan = self.mgr.start(ACTION_PLAN1['uuid'])
        expect = [('POST', '/v1/action_plans/%s/start'
                   % ACTION_PLAN1['uuid'], {}, {})]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_STATE, action_plan.state)
