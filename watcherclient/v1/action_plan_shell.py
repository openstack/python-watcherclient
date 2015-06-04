# -*- coding: utf-8 -*-
#
# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

# import argparse

from oslo_utils import uuidutils
from watcherclient.common import utils
from watcherclient.openstack.common.apiclient.exceptions import ValidationError
from watcherclient.openstack.common import cliutils
from watcherclient.v1 import resource_fields as res_fields


def _print_action_plan_show(action_plan):
    fields = res_fields.ACTION_PLAN_FIELDS
    data = dict([(f, getattr(action_plan, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'action-plan',
    metavar='<action-plan>',
    help="UUID of the action_plan.")
def do_action_plan_show(cc, args):
    """Show detailed information about an action plan."""
    action_plan_uuid = getattr(args, 'action-plan')
    if uuidutils.is_uuid_like(action_plan_uuid):
        action_plan = cc.action_plan.get(action_plan_uuid)
        _print_action_plan_show(action_plan)
    else:
        raise ValidationError()


@cliutils.arg(
    '--audit',
    metavar='<audit>',
    help='UUID of an audit used for filtering.')
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about action plans.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of action plans to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Watcher API Service.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Action Plan field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
def do_action_plan_list(cc, args):
    """List the action plans."""
    params = {}

    if args.audit is not None:
        params['audit'] = args.audit
    if args.detail:
        fields = res_fields.ACTION_PLAN_FIELDS
        field_labels = res_fields.ACTION_PLAN_FIELD_LABELS
    else:
        fields = res_fields.ACTION_PLAN_SHORT_LIST_FIELDS
        field_labels = res_fields.ACTION_PLAN_SHORT_LIST_FIELD_LABELS

    params.update(utils.common_params_for_list(args,
                                               fields,
                                               field_labels))

    action_plan = cc.action_plan.list(**params)
    cliutils.print_list(action_plan, fields,
                        field_labels=field_labels,
                        sortby_index=None)


@cliutils.arg(
    'action-plan',
    metavar='<action-plan>',
    nargs='+',
    help="UUID of the action plan.")
def do_action_plan_delete(cc, args):
    """Delete an action plan."""
    for p in getattr(args, 'action-plan'):
        if uuidutils.is_uuid_like(p):
            cc.action_plan.delete(p)
            print ('Deleted action plan %s' % p)
        else:
            raise ValidationError()


@cliutils.arg(
    'action-plan',
    metavar='<action-plan>',
    help="UUID of the action plan.")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operation: 'add', 'replace', or 'remove'.")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attribute to add, replace, or remove. Can be specified multiple  "
         "times. For 'remove', only <path> is necessary.")
def do_action_plan_update(cc, args):
    """Update information about an action plan."""
    action_plan_uuid = getattr(args, 'action-plan')
    if uuidutils.is_uuid_like(action_plan_uuid):
        patch = utils.args_array_to_patch(args.op, args.attributes[0])
        action_plan = cc.action_plan.update(action_plan_uuid, patch)
        _print_action_plan_show(action_plan)
    else:
        raise ValidationError()


@cliutils.arg('action-plan',
              metavar='<action-plan>',
              help="UUID of the action plan.")
def do_action_plan_start(cc, args):
    """Execute an action plan."""
    action_plan_uuid = getattr(args, 'action-plan')
    if uuidutils.is_uuid_like(action_plan_uuid):
        args.op = 'replace'
        args.attributes = [['state=STARTING']]

        patch = utils.args_array_to_patch(
            args.op,
            args.attributes[0])

        action_plan = cc.action_plan.update(action_plan_uuid, patch)
        _print_action_plan_show(action_plan)
    else:
        raise ValidationError()
