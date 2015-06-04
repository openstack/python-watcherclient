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

# import argparse

from watcherclient.common import utils
from watcherclient.openstack.common import cliutils
from watcherclient.v1 import resource_fields as res_fields


def _print_metric_collector_show(metric_collector):
    fields = res_fields.METRIC_COLLECTOR_FIELDS
    data = dict([(f, getattr(metric_collector, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'metric_collector',
    metavar='<metric_collector>',
    help="UUID of the metric collector")
def do_metric_collector_show(cc, args):
    """Show detailed information about a metric collector."""
    metric_collector = cc.metric_collector.get(args.metric_collector)
    _print_metric_collector_show(metric_collector)


@cliutils.arg(
    '--category',
    metavar='<category>',
    help='Only show information for metric collectors with this category.')
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about metric collectors.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of metric collectors to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Watcher API Service.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Metric collector field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
def do_metric_collector_list(cc, args):
    """List the metric collectors."""
    params = {}

    if args.detail:
        fields = res_fields.METRIC_COLLECTOR_FIELDS
        field_labels = res_fields.METRIC_COLLECTOR_FIELD_LABELS
    else:
        fields = res_fields.METRIC_COLLECTOR_SHORT_LIST_FIELDS
        field_labels = res_fields.METRIC_COLLECTOR_SHORT_LIST_FIELD_LABELS

    params.update(utils.common_params_for_list(args,
                                               fields,
                                               field_labels))

    metric_collector = cc.metric_collector.list(**params)
    cliutils.print_list(metric_collector, fields,
                        field_labels=field_labels,
                        sortby_index=None)


@cliutils.arg(
    '-c', '--category',
    metavar='<category>',
    required=True,
    help='Metric category.')
@cliutils.arg(
    '-e', '--endpoint-url',
    required=True,
    metavar='<goal>',
    help='URL towards which publish metric data.')
def do_metric_collector_create(cc, args):
    """Create a new metric collector."""
    field_list = ['category', 'endpoint']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    metric_collector = cc.metric_collector.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(metric_collector, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'metric_collector',
    metavar='<metric_collector>',
    nargs='+',
    help="UUID of the metric collector.")
def do_metric_collector_delete(cc, args):
    """Delete a metric collector."""
    for p in args.metric_collector:
        cc.metric_collector.delete(p)
        print ('Deleted metric collector %s' % p)


@cliutils.arg(
    'metric_collector',
    metavar='<metric_collector>',
    help="UUID of the metric collector.")
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
def do_metric_collector_update(cc, args):
    """Update information about a metric collector."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    metric_collector = cc.metric_collector.update(
        getattr(args, 'metric-collector'), patch)
    _print_metric_collector_show(metric_collector)
