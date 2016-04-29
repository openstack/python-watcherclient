# -*- coding: utf-8 -*-
#
# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from watcherclient.common import cliutils
from watcherclient.common import utils
from watcherclient.v1 import resource_fields as res_fields


def _print_strategy_show(strategy):
    fields = res_fields.STRATEGY_FIELDS
    data = dict([(f, getattr(strategy, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'strategy',
    metavar='<strategy>',
    help="UUID or name of the strategy")
def do_strategy_show(cc, args):
    """Show detailed information about a _print_strategy_show."""
    strategy = cc.strategy.get(args.strategy)
    _print_strategy_show(strategy)


@cliutils.arg(
    '--goal-uuid',
    metavar='<goal_uuid>',
    dest='goal_uuid',
    help='UUID of the goal')
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about each strategy.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of strategies to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Watcher API Service.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Goal field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
def do_strategy_list(cc, args):
    """List the strategies."""
    params = {}

    if args.detail:
        fields = res_fields.STRATEGY_FIELDS
        field_labels = res_fields.STRATEGY_FIELD_LABELS
    else:
        fields = res_fields.STRATEGY_SHORT_LIST_FIELDS
        field_labels = res_fields.STRATEGY_SHORT_LIST_FIELD_LABELS

    if args.goal_uuid:
        params["goal_uuid"] = args.goal_uuid

    params.update(utils.common_params_for_list(args,
                                               fields,
                                               field_labels))

    strategy = cc.strategy.list(**params)
    cliutils.print_list(strategy, fields,
                        field_labels=field_labels,
                        sortby_index=None)