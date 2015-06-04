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


def _print_audit_template_show(audit_template):
    fields = res_fields.AUDIT_TEMPLATE_FIELDS
    data = dict([(f, getattr(audit_template, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'audit-template',
    metavar='<audit-template>',
    help="Name or UUID of the audit template.")
def do_audit_template_show(cc, args):
    """Show detailed information about a audit template."""

    audit_template = cc.audit_template.get(getattr(args, 'audit-template'))
    _print_audit_template_show(audit_template)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about audit templates.")
@cliutils.arg(
    '--name',
    metavar='<name>',
    help='Only show information for the audit template with this name.')
@cliutils.arg(
    '--goal',
    metavar='<goal>',
    help='Name the goal used for filtering.')
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of audit templates to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Watcher API Service.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Audit template field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
def do_audit_template_list(cc, args):
    """List the audit templates."""
    params = {}

    if args.name is not None:
        params['name'] = args.name
    if args.goal is not None:
        params['goal'] = args.goal
    if args.detail:
        fields = res_fields.AUDIT_TEMPLATE_FIELDS
        field_labels = res_fields.AUDIT_TEMPLATE_FIELD_LABELS
    else:
        fields = res_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELDS
        field_labels = res_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELD_LABELS

    params.update(utils.common_params_for_list(args,
                                               fields,
                                               field_labels))

    audit_template = cc.audit_template.list(**params)
    cliutils.print_list(audit_template, fields,
                        field_labels=field_labels,
                        sortby_index=None)


@cliutils.arg(
    'name',
    metavar='<name>',
    help='Name for this audit template.')
@cliutils.arg(
    'goal',
    metavar='<goal>',
    help='Goal Type associated to this audit template.')
@cliutils.arg(
    '-d', '--description',
    metavar='<description>',
    help='Descrition of the audit template.')
@cliutils.arg(
    '-e', '--extra',
    metavar='<key=value>',
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")
@cliutils.arg(
    '-a', '--host-aggregate',
    dest='host_aggregate',
    metavar='<host-aggregate>',
    help='Name or ID of the host aggregate targeted by this audit template.')
def do_audit_template_create(cc, args):
    """Create a new audit template."""
    field_list = ['host_aggregate', 'description', 'name', 'extra', 'goal']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    audit_template = cc.audit_template.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(audit_template, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'audit-template',
    metavar='<audit-template>',
    nargs='+',
    help="UUID or name of the audit template.")
def do_audit_template_delete(cc, args):
    """Delete an audit template."""
    for p in getattr(args, 'audit-template'):
        cc.audit_template.delete(p)
        print ('Deleted audit template %s' % p)


@cliutils.arg(
    'audit-template',
    metavar='<audit-template>',
    help="UUID or name of the audit template.")
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
def do_audit_template_update(cc, args):
    """Update information about an audit template."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    audit_template = cc.audit_template.update(getattr(args, 'audit-template'),
                                              patch)
    _print_audit_template_show(audit_template)
