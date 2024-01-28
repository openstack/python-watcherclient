#   Copyright 2016 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import abc
import logging

from cliff import command
from cliff import lister
from cliff import show


class CommandMeta(abc.ABCMeta):

    def __new__(mcs, name, bases, cls_dict):
        if 'log' not in cls_dict:
            cls_dict['log'] = logging.getLogger(
                cls_dict['__module__'] + '.' + name)
        return super(CommandMeta, mcs).__new__(mcs, name, bases, cls_dict)


class Command(command.Command, metaclass=CommandMeta):

    def run(self, parsed_args):
        self.log.debug('run(%s)', parsed_args)
        return super(Command, self).run(parsed_args)


class Lister(Command, lister.Lister):
    pass


class ShowOne(Command, show.ShowOne):
    def get_parser(self, prog_name, formatter_class=None):
        parser = super(ShowOne, self).get_parser(prog_name)
        if formatter_class:
            parser.formatter_class = formatter_class
        return parser
