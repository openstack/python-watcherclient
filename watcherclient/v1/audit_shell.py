# Copyright (c) 2016 b<>com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from osc_lib import utils
from oslo_utils import uuidutils

from watcherclient._i18n import _
from watcherclient.common import api_versioning
from watcherclient.common import command
from watcherclient.common import utils as common_utils
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


def drop_unsupported_field(app_args, fields, field_labels):
    fields = copy.copy(fields)
    field_labels = copy.copy(field_labels)
    api_ver = app_args.os_infra_optim_api_version
    if not api_versioning.allow_start_end_audit_time(api_ver):
        for field, label in zip(('start_time', 'end_time'),
                                ('Start Time', 'End Time')):
            fields.remove(field)
            field_labels.remove(label)
    if not api_versioning.launch_audit_forced(api_ver):
        fields.remove('force')
        field_labels.remove('Force')
    return fields, field_labels


class ShowAudit(command.ShowOne):
    """Show detailed information about a given audit."""

    def get_parser(self, prog_name):
        parser = super(ShowAudit, self).get_parser(prog_name)
        parser.add_argument(
            'audit',
            metavar='<audit>',
            help=_('UUID or name of the audit'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        try:
            audit = client.audit.get(parsed_args.audit)
            if audit.strategy_name is None:
                audit.strategy_name = 'auto'
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))

        columns = res_fields.AUDIT_FIELDS
        column_headers = res_fields.AUDIT_FIELD_LABELS
        columns, column_headers = drop_unsupported_field(
            self.app_args, columns, column_headers)

        return column_headers, utils.get_item_properties(audit, columns)


class ListAudit(command.Lister):
    """List information on retrieved audits."""

    def get_parser(self, prog_name):
        parser = super(ListAudit, self).get_parser(prog_name)
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about audits."))
        parser.add_argument(
            '--goal',
            dest='goal',
            metavar='<goal>',
            help=_('UUID or name of the goal used for filtering.'))
        parser.add_argument(
            '--strategy',
            dest='strategy',
            metavar='<strategy>',
            help=_('UUID or name of the strategy used for filtering.'))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of audits to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Watcher API Service.'))
        parser.add_argument(
            '--sort-key',
            metavar='<field>',
            help=_('Audit field that will be used for sorting.'))
        parser.add_argument(
            '--sort-dir',
            metavar='<direction>',
            choices=['asc', 'desc'],
            help=_('Sort direction: "asc" (the default) or "desc".'))
        parser.add_argument(
            '--marker',
            dest='marker',
            metavar='<marker>',
            default=None,
            help=_('UUID of the last audit in the previous page; '
                   'displays list of audits after "marker".'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}

        # Optional
        if parsed_args.goal:
            params['goal'] = parsed_args.goal

        # Optional
        if parsed_args.strategy:
            params['strategy'] = parsed_args.strategy

        if parsed_args.detail:
            fields = res_fields.AUDIT_FIELDS
            field_labels = res_fields.AUDIT_FIELD_LABELS
        else:
            fields = res_fields.AUDIT_SHORT_LIST_FIELDS
            field_labels = res_fields.AUDIT_SHORT_LIST_FIELD_LABELS

        if parsed_args.detail:
            fields, field_labels = drop_unsupported_field(
                self.app_args, fields, field_labels)

        params.update(common_utils.common_params_for_list(
            parsed_args, fields, field_labels))

        try:
            data = client.audit.list(**params)
            for audit in data:
                if audit.strategy_name is None:
                    audit.strategy_name = 'auto'
        except exceptions.HTTPNotFound as ex:
            raise exceptions.CommandError(str(ex))

        return (field_labels,
                (utils.get_item_properties(item, fields) for item in data))


class CreateAudit(command.ShowOne):
    """Create new audit."""

    def get_parser(self, prog_name):
        parser = super(CreateAudit, self).get_parser(prog_name)
        parser.add_argument(
            '-t', '--audit_type',
            dest='audit_type',
            metavar='<audit_type>',
            default='ONESHOT',
            choices=['ONESHOT', 'CONTINUOUS'],
            help=_("Audit type. It must be ONESHOT or CONTINUOUS. "
                   "Default is ONESHOT."))
        parser.add_argument(
            '-p', '--parameter',
            dest='parameters',
            metavar='<name=value>',
            action='append',
            help=_("Record strategy parameter/value metadata. "
                   "Can be specified multiple times."))
        parser.add_argument(
            '-i', '--interval',
            dest='interval',
            metavar='<interval>',
            help=_('Audit interval (in seconds or cron format). '
                   'Cron interval can be used like: ``*/5 * * * *``. '
                   'Only used if the audit is CONTINUOUS.'))
        parser.add_argument(
            '-g', '--goal',
            dest='goal',
            metavar='<goal>',
            help=_('Goal UUID or name associated to this audit.'))
        parser.add_argument(
            '-s', '--strategy',
            dest='strategy',
            metavar='<strategy>',
            help=_('Strategy UUID or name associated to this audit.'))
        parser.add_argument(
            '-a', '--audit-template',
            dest='audit_template_uuid',
            metavar='<audit_template>',
            help=_('Audit template used for this audit (name or uuid).'))
        parser.add_argument(
            '--auto-trigger',
            dest='auto_trigger',
            action='store_true',
            default=False,
            help=_('Trigger automatically action plan '
                   'once audit is succeeded.'))
        parser.add_argument(
            '--name',
            dest='name',
            metavar='<name>',
            help=_('Name for this audit.'))
        parser.add_argument(
            '--start-time',
            dest='start_time',
            metavar='<start_time>',
            help=_('CONTINUOUS audit local start time. '
                   'Format: YYYY-MM-DD hh:mm:ss'))
        parser.add_argument(
            '--end-time',
            dest='end_time',
            metavar='<end_time>',
            help=_('CONTINUOUS audit local end time. '
                   'Format: YYYY-MM-DD hh:mm:ss'))
        parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            help=_('Launch audit even if action plan '
                   'is ongoing. default is False'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        field_list = ['audit_template_uuid', 'audit_type', 'parameters',
                      'interval', 'goal', 'strategy', 'auto_trigger',
                      'name']

        api_ver = self.app_args.os_infra_optim_api_version
        if api_versioning.allow_start_end_audit_time(api_ver):
            if parsed_args.start_time is not None:
                field_list.append('start_time')
            if parsed_args.end_time is not None:
                field_list.append('end_time')
        if api_versioning.launch_audit_forced(api_ver):
            if parsed_args.force is not None:
                field_list.append('force')

        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = common_utils.args_array_to_dict(fields, 'parameters')

        if fields.get('audit_template_uuid'):
            if not uuidutils.is_uuid_like(fields['audit_template_uuid']):
                fields['audit_template_uuid'] = client.audit_template.get(
                    fields['audit_template_uuid']).uuid

        audit = client.audit.create(**fields)
        if audit.strategy_name is None:
            audit.strategy_name = 'auto'

        columns = res_fields.AUDIT_FIELDS
        column_headers = res_fields.AUDIT_FIELD_LABELS
        columns, column_headers = drop_unsupported_field(
            self.app_args, columns, column_headers)

        return column_headers, utils.get_item_properties(audit, columns)


class UpdateAudit(command.ShowOne):
    """Update audit command."""

    def get_parser(self, prog_name):
        parser = super(UpdateAudit, self).get_parser(prog_name)
        parser.add_argument(
            'audit',
            metavar='<audit>',
            help=_("UUID or name of the audit."))
        parser.add_argument(
            'op',
            metavar='<op>',
            choices=['add', 'replace', 'remove'],
            help=_("Operation: 'add', 'replace', or 'remove'."))
        parser.add_argument(
            'attributes',
            metavar='<path=value>',
            nargs='+',
            action='append',
            default=[],
            help=_("Attribute to add, replace, or remove. Can be specified "
                   "multiple times. For 'remove', only <path> is necessary."))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        patch = common_utils.args_array_to_patch(
            parsed_args.op, parsed_args.attributes[0],
            exclude_fields=['/interval'])

        audit = client.audit.update(parsed_args.audit, patch)

        columns = res_fields.AUDIT_FIELDS
        column_headers = res_fields.AUDIT_FIELD_LABELS

        columns, column_headers = drop_unsupported_field(
            self.app_args, columns, column_headers)

        return column_headers, utils.get_item_properties(audit, columns)


class DeleteAudit(command.Command):
    """Delete audit command."""

    def get_parser(self, prog_name):
        parser = super(DeleteAudit, self).get_parser(prog_name)
        parser.add_argument(
            'audits',
            metavar='<audit>',
            nargs='+',
            help=_('UUID or name of the audit'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        for audit in parsed_args.audits:
            client.audit.delete(audit)
