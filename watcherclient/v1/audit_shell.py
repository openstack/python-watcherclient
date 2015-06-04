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


def _print_audit_show(audit):
    fields = res_fields.AUDIT_FIELDS
    data = dict([(f, getattr(audit, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'audit',
    metavar='<audit>',
    help="UUID of the audit.")
def do_audit_show(cc, args):
    """Show detailed information about an audit."""

    if uuidutils.is_uuid_like(args.audit):
        audit = cc.audit.get(args.audit)
        _print_audit_show(audit)
    else:
        raise ValidationError()


@cliutils.arg(
    '--audit-template',
    metavar='<audit_template>',
    dest='audit_template',
    help='Name or UUID of an audit template used for filtering.')
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about audits.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of audits to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Watcher API Service.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Audit field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
def do_audit_list(cc, args):
    """List the audits."""
    params = {}

    if args.audit_template is not None:
        params['audit_template'] = args.audit_template
    if args.detail:
        fields = res_fields.AUDIT_FIELDS
        field_labels = res_fields.AUDIT_FIELD_LABELS
    else:
        fields = res_fields.AUDIT_SHORT_LIST_FIELDS
        field_labels = res_fields.AUDIT_SHORT_LIST_FIELD_LABELS

    # params.update(utils.common_params_for_list(args, fields, field_labels))

    audit = cc.audit.list(**params)
    cliutils.print_list(audit, fields,
                        field_labels=field_labels,
                        sortby_index=None)


@cliutils.arg(
    '-a', '--audit-template',
    required=True,
    dest='audit_template_uuid',
    metavar='<audit_template>',
    help='Audit template used for this audit (name or uuid).')
@cliutils.arg(
    '-d', '--deadline',
    dest='deadline',
    metavar='<deadline>',
    help='Descrition of the audit.')
@cliutils.arg(
    '-t', '--type',
    dest='type',
    metavar='<type>',
    default='ONESHOT',
    help="Audit type.")
def do_audit_create(cc, args):
    """Create a new audit."""
    field_list = ['audit_template_uuid', 'type', 'deadline']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    audit = cc.audit.create(**fields)
    field_list.append('uuid')
    data = dict([(f, getattr(audit, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'audit',
    metavar='<audit>',
    nargs='+',
    help="UUID of the audit.")
def do_audit_delete(cc, args):
    """Delete an audit."""
    for p in args.audit:
        if uuidutils.is_uuid_like(p):
            cc.audit.delete(p)
            print ('Deleted audit %s' % p)
        else:
            raise ValidationError()


@cliutils.arg(
    'audit',
    metavar='<audit>',
    help="UUID of the audit.")
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
def do_audit_update(cc, args):
    """Update information about an audit."""
    if uuidutils.is_uuid_like(args.audit):
        patch = utils.args_array_to_patch(args.op, args.attributes[0])
        audit = cc.audit.update(args.audit, patch)
        _print_audit_show(audit)
    else:
        raise ValidationError()
