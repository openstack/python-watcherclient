#
# Copyright 2012 OpenStack LLC.
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

import argparse
import os
import uuid
import yaml

from oslo_serialization import jsonutils
from oslo_utils import importutils

from watcherclient._i18n import _
from watcherclient import exceptions as exc


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


def define_command(subparsers, command, callback, cmd_mapper):
    '''Define a command in the subparsers collection.

    :param subparsers: subparsers collection where the command will go
    :param command: command name
    :param callback: function that will be used to process the command
    '''
    desc = callback.__doc__ or ''
    help = desc.strip().split('\n')[0]
    arguments = getattr(callback, 'arguments', [])

    subparser = subparsers.add_parser(command, help=help,
                                      description=desc,
                                      add_help=False,
                                      formatter_class=HelpFormatter)
    subparser.add_argument('-h', '--help', action='help',
                           help=argparse.SUPPRESS)
    cmd_mapper[command] = subparser
    for (args, kwargs) in arguments:
        subparser.add_argument(*args, **kwargs)
    subparser.set_defaults(func=callback)


def define_commands_from_module(subparsers, command_module, cmd_mapper):
    """Add *do_* methods in a module and add as commands into a subparsers."""

    for method_name in (a for a in dir(command_module) if a.startswith('do_')):
        # Commands should be hypen-separated instead of underscores.
        command = method_name[3:].replace('_', '-')
        callback = getattr(command_module, method_name)
        define_command(subparsers, command, callback, cmd_mapper)


def import_versioned_module(version, submodule=None):
    module = 'watcherclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def split_and_deserialize(string, exclude_fields=[]):
    """Split and try to JSON deserialize a string.

    Gets a string with the KEY=VALUE format, split it (using '=' as the
    separator) and try to JSON deserialize the VALUE.

    :returns: A tuple of (key, value).
    """
    try:
        key, value = string.split("=", 1)
    except ValueError:
        raise exc.CommandError(_('Attributes must be a list of '
                                 'PATH=VALUE not "%s"') % string)
    if key not in exclude_fields:
        try:
            value = jsonutils.loads(value)
        except ValueError:
            pass

    return (key, value)


def args_array_to_dict(kwargs, key_to_convert):
    values_to_convert = kwargs.get(key_to_convert)
    if values_to_convert:
        kwargs[key_to_convert] = dict(split_and_deserialize(v)
                                      for v in values_to_convert)
    return kwargs


def args_array_to_patch(op, attributes, exclude_fields=[]):
    patch = []
    for attr in attributes:
        # Sanitize
        if not attr.startswith('/'):
            attr = '/' + attr

        if op in ['add', 'replace']:
            path, value = split_and_deserialize(attr,
                                                exclude_fields=exclude_fields)
            patch.append({'op': op, 'path': path, 'value': value})

        elif op == "remove":
            # For remove only the key is needed
            patch.append({'op': op, 'path': attr})
        else:
            raise exc.CommandError(_('Unknown PATCH operation: %s') % op)
    return patch


def common_params_for_list(args, fields, field_labels):
    """Generate 'params' dict that is common for every 'list' command.

    :param args: arguments from command line.
    :param fields: possible fields for sorting.
    :param field_labels: possible field labels for sorting.
    :returns: a dict with params to pass to the client method.
    """
    params = {}
    if args.limit is not None:
        if args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') % args.limit)
        params['limit'] = args.limit

    if args.sort_key is not None:
        # Support using both heading and field name for sort_key
        fields_map = dict(zip(field_labels, fields))
        fields_map.update(zip(fields, fields))
        try:
            sort_key = fields_map[args.sort_key]
        except KeyError:
            raise exc.CommandError(
                _("%(sort_key)s is an invalid field for sorting, "
                  "valid values for --sort-key are: %(valid)s") %
                {'sort_key': args.sort_key,
                 'valid': list(fields_map)})
        params['sort_key'] = sort_key
    if args.sort_dir is not None:
        if args.sort_dir not in ('asc', 'desc'):
            raise exc.CommandError(
                _("%s is an invalid value for sort direction, "
                  "valid values for --sort-dir are: 'asc', 'desc'") %
                args.sort_dir)
        params['sort_dir'] = args.sort_dir

    marker = getattr(args, 'marker', None)
    if marker is not None:
        params['marker'] = marker
    params['detail'] = args.detail

    return params


def common_filters(limit=None, sort_key=None, sort_dir=None, marker=None):
    """Generate common filters for any list request.

    :param limit: maximum number of entities to return.
    :param sort_key: field to use for sorting.
    :param sort_dir: direction of sorting: 'asc' or 'desc'.
    :param marker: The last actionplan UUID of the previous page.
    :returns: list of string filters.
    """
    filters = []
    if isinstance(limit, int) and limit > 0:
        filters.append('limit=%s' % limit)
    if sort_key is not None:
        filters.append('sort_key=%s' % sort_key)
    if sort_dir is not None:
        filters.append('sort_dir=%s' % sort_dir)
    if marker is not None:
        filters.append('marker=%s' % marker)
    return filters


def is_uuid_like(val):
    """Returns validation of a value as a UUID.

    For our purposes, a UUID is a canonical form string:
    aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa

    """
    try:
        return str(uuid.UUID(val)) == val
    except (TypeError, ValueError, AttributeError):
        return False


def serialize_file_to_dict(filename):
    filename = os.path.expanduser(filename)
    with open(filename, "rb") as stream:
        scope = yaml.safe_load(stream.read())
    return scope
