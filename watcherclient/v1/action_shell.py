# -*- coding: utf-8 -*-
#
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

# import argparse

from oslo_utils import uuidutils
from watcherclient.common import utils
from watcherclient.openstack.common.apiclient.exceptions import ValidationError
from watcherclient.openstack.common import cliutils
from watcherclient.v1 import resource_fields as res_fields


def _print_action_show(action):
    fields = res_fields.ACTION_FIELDS
    data = dict([(f, getattr(action, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'action',
    metavar='<action>',
    help="UUID of the action")
def do_action_show(cc, args):
    """Show detailed information about an action."""
    if uuidutils.is_uuid_like(args.action):
        action = cc.action.get(args.action)
        _print_action_show(action)
    else:
        raise ValidationError()


@cliutils.arg(
    '--action-plan',
    metavar='<action_plan>',
    help='UUID of the action plan used for filtering.')
@cliutils.arg(
    '--audit',
    metavar='<audit>',
    help=' UUID of the audit used for filtering.')
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about actions.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of actions to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Watcher API Service.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Action field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
def do_action_list(cc, args):
    """List the actions."""
    params = {}

    if args.action_plan is not None:
        params['action_plan'] = args.action_plan
    if args.audit is not None:
        params['audit'] = args.audit
    if args.detail:
        fields = res_fields.ACTION_FIELDS
        field_labels = res_fields.ACTION_FIELD_LABELS
    else:
        fields = res_fields.ACTION_SHORT_LIST_FIELDS
        field_labels = res_fields.ACTION_SHORT_LIST_FIELD_LABELS

    params.update(utils.common_params_for_list(args,
                                               fields,
                                               field_labels))

    action = cc.action.list(**params)
    cliutils.print_list(action, fields,
                        field_labels=field_labels,
                        sortby_index=None)


@cliutils.arg(
    'action',
    metavar='<action>',
    nargs='+',
    help="UUID of the action.")
def do_action_delete(cc, args):
    """Delete an action."""
    for p in args.action:
        if uuidutils.is_uuid_like(p):
            cc.action.delete(p)
            print ('Deleted action %s' % p)
        else:
            raise ValidationError()


@cliutils.arg('action', metavar='<action>', help="UUID of the action.")
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
def do_action_update(cc, args):
    """Update information about an action."""
    if uuidutils.is_uuid_like(args.action):
        patch = utils.args_array_to_patch(args.op, args.attributes[0])
        action = cc.action.update(args.action, patch)
        _print_action_show(action)
    else:
        raise ValidationError()
