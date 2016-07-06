# -*- encoding: utf-8 -*-
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

from cliff.formatters import yaml_format
from openstackclient.common import utils
from oslo_utils import uuidutils
import six

from watcherclient._i18n import _
from watcherclient.common import command
from watcherclient.common import utils as common_utils
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


def format_global_efficacy(global_efficacy):
    formatted_global_efficacy = None
    if (global_efficacy.get('value') is not None and
            global_efficacy.get('unit')):
        formatted_global_efficacy = "%(value)s %(unit)s" % dict(
            unit=global_efficacy.get('unit'),
            value=global_efficacy.get('value'))
    elif global_efficacy.get('value') is not None:
        formatted_global_efficacy = global_efficacy.get('value')

    return formatted_global_efficacy


class ShowActionPlan(command.ShowOne):
    """Show detailed information about a given action plan."""

    def get_parser(self, prog_name):
        parser = super(ShowActionPlan, self).get_parser(prog_name)
        parser.add_argument(
            'action_plan',
            metavar='<action-plan>',
            help=_('UUID of the action plan'),
        )
        return parser

    def _format_indicators(self, action_plan, parsed_args):
        out = six.StringIO()
        efficacy_indicators = action_plan.efficacy_indicators
        fields = ['name', 'description', 'value', 'unit']
        yaml_format.YAMLFormatter().emit_list(
            column_names=list(field.capitalize()
                              for field in fields),
            data=[utils.get_dict_properties(spec, fields)
                  for spec in efficacy_indicators],
            stdout=out,
            parsed_args=parsed_args,
            )
        return out.getvalue() or ''

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        action_plan_uuid = parsed_args.action_plan

        if not uuidutils.is_uuid_like(action_plan_uuid):
            raise exceptions.ValidationError()

        try:
            action_plan = client.action_plan.get(action_plan_uuid)
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))

        if parsed_args.formatter == 'table':
            # Update the raw efficacy indicators with the formatted ones
            action_plan.efficacy_indicators = (
                self._format_indicators(action_plan, parsed_args))

            # Update the raw global efficacy with the formatted one
            action_plan.global_efficacy = format_global_efficacy(
                action_plan.global_efficacy)

        columns = res_fields.ACTION_PLAN_FIELDS
        column_headers = res_fields.ACTION_PLAN_FIELD_LABELS
        return column_headers, utils.get_item_properties(action_plan, columns)


class ListActionPlan(command.Lister):
    """List information on retrieved action plans."""

    def get_parser(self, prog_name):
        parser = super(ListActionPlan, self).get_parser(prog_name)
        parser.add_argument(
            '--audit',
            metavar='<audit>',
            help=_('UUID of an audit used for filtering.'))
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about action plans."))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of action plans to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Watcher API Service.'))
        parser.add_argument(
            '--sort-key',
            metavar='<field>',
            help=_('Action Plan field that will be used for sorting.'))
        parser.add_argument(
            '--sort-dir',
            metavar='<direction>',
            choices=['asc', 'desc'],
            help=_('Sort direction: "asc" (the default) or "desc".'))

        return parser

    def _format_indicators(self, action_plan, parsed_args):
        out = six.StringIO()
        efficacy_indicators = action_plan.efficacy_indicators
        fields = ['name', 'value', 'unit']
        yaml_format.YAMLFormatter().emit_list(
            column_names=list(field.capitalize()
                              for field in fields),
            data=[utils.get_dict_properties(spec, fields)
                  for spec in efficacy_indicators],
            stdout=out,
            parsed_args=parsed_args,
            )
        return out.getvalue() or ''

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}
        if parsed_args.audit is not None:
            params['audit'] = parsed_args.audit
        if parsed_args.detail:
            fields = res_fields.ACTION_PLAN_FIELDS
            field_labels = res_fields.ACTION_PLAN_FIELD_LABELS
        else:
            fields = res_fields.ACTION_PLAN_SHORT_LIST_FIELDS
            field_labels = res_fields.ACTION_PLAN_SHORT_LIST_FIELD_LABELS

        params.update(common_utils.common_params_for_list(
            parsed_args, fields, field_labels))

        data = client.action_plan.list(**params)

        if parsed_args.formatter == 'table':
            for action_plan in data:
                # Update the raw efficacy indicators with the formatted ones
                action_plan.efficacy_indicators = (
                    self._format_indicators(action_plan, parsed_args))

                # Update the raw global efficacy with the formatted one
                action_plan.global_efficacy = format_global_efficacy(
                    action_plan.global_efficacy)

        return (field_labels,
                (utils.get_item_properties(item, fields) for item in data))


class CreateActionPlan(command.ShowOne):
    """Create new audit."""

    def get_parser(self, prog_name):
        parser = super(CreateActionPlan, self).get_parser(prog_name)
        parser.add_argument(
            '-a', '--audit-template',
            required=True,
            dest='audit_template_uuid',
            metavar='<audit_template>',
            help=_('ActionPlan template used for this audit (name or uuid).'))
        parser.add_argument(
            '-d', '--deadline',
            dest='deadline',
            metavar='<deadline>',
            help=_('Descrition of the audit.'))
        parser.add_argument(
            '-t', '--audit_type',
            dest='audit_type',
            metavar='<audit_type>',
            default='ONESHOT',
            help=_("ActionPlan type."))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        field_list = ['audit_template_uuid', 'audit_type', 'deadline']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        if fields.get('audit_template_uuid'):
            if not uuidutils.is_uuid_like(fields['audit_template_uuid']):
                fields['audit_template_uuid'] = client.audit_template.get(
                    fields['audit_template_uuid']).uuid

        audit = client.audit.create(**fields)

        columns = res_fields.ACTION_PLAN_FIELDS
        column_headers = res_fields.ACTION_PLAN_FIELD_LABELS

        return column_headers, utils.get_item_properties(audit, columns)


class UpdateActionPlan(command.ShowOne):
    """Update action plan command."""

    def get_parser(self, prog_name):
        parser = super(UpdateActionPlan, self).get_parser(prog_name)
        parser.add_argument(
            'action_plan',
            metavar='<action-plan>',
            help=_("UUID of the action_plan."))
        parser.add_argument(
            'op',
            metavar='<op>',
            choices=['add', 'replace', 'remove'],
            help=_("Operation: 'add'), 'replace', or 'remove'."))
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

        if not uuidutils.is_uuid_like(parsed_args.action_plan):
            raise exceptions.ValidationError()

        patch = common_utils.args_array_to_patch(
            parsed_args.op, parsed_args.attributes[0])

        action_plan = client.action_plan.update(parsed_args.action_plan, patch)

        columns = res_fields.ACTION_PLAN_FIELDS
        column_headers = res_fields.ACTION_PLAN_FIELD_LABELS

        return column_headers, utils.get_item_properties(action_plan, columns)


class StartActionPlan(command.ShowOne):
    """Start action plan command."""

    def get_parser(self, prog_name):
        parser = super(StartActionPlan, self).get_parser(prog_name)
        parser.add_argument(
            'action_plan',
            metavar='<action-plan>',
            help=_("UUID of the action_plan."))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        if not uuidutils.is_uuid_like(parsed_args.action_plan):
            raise exceptions.ValidationError()

        action_plan = client.action_plan.start(parsed_args.action_plan)

        columns = res_fields.ACTION_PLAN_FIELDS
        column_headers = res_fields.ACTION_PLAN_FIELD_LABELS

        return column_headers, utils.get_item_properties(action_plan, columns)


class DeleteActionPlan(command.Command):
    """Delete action plan command."""

    def get_parser(self, prog_name):
        parser = super(DeleteActionPlan, self).get_parser(prog_name)
        parser.add_argument(
            'action_plans',
            metavar='<action-plan>',
            nargs='+',
            help=_('UUID of the action plan'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        for action_plan in parsed_args.action_plans:
            if not uuidutils.is_uuid_like(action_plan):
                raise exceptions.ValidationError()

            client.action_plan.delete(action_plan)
