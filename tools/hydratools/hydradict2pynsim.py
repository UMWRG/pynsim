#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#    (c) Copyright 2015
#    Eawag, Swiss Federal Institute of Aquatic Science and Technology
#
#    This file is part of pynsim.
#
#    pynsim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pynsim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pynsim.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

from jinja2 import Environment, FileSystemLoader
from hydra_client import JSONConnection
from lxml import etree

import argparse as ap


class HydraTemplateToPynsim(object):


    def __init__(self, input_template, output=None):


        self.type_to_class_conversion = dict(NODE='Node',
                                     LINK='Link',
                                     NETWORK='Network',
                                     GROUP='Institution',
                                     )

        if output is None:
            self.output, ext = os.path.splitext(self.inputfile)
        else:
            self.output = os.path.abspath(os.path.expanduser(output))

        self.input_template = input_template
        self.parsed_template = {'Node': [], 'Link': [], 'Institution': [], 'Network': []}

        self.basepath = os.path.dirname(os.path.abspath(__file__))
        self.attr_lookup = []

        self.conn = JSONConnection()
        self.conn.login(username='root', password='')

    def load_template(self):

        try:
            float(self.input_template)
            template_id = self.input_template
            self.input_dict = self.conn.get_template_as_dict(int(template_id))
        except ValueError:
            try:
                self.input_file = os.path.abspath(os.path.expanduser(input_file))
                self.input_dict = json.load(self.input_file) 
            except:

                self.input_dict  = self.conn.get_template_by_name(input_template)


        return self.input_dict

    def parse_template(self):

        self.attr_lookup = self.input_dict['attributes']
        self.dataset_lookup = self.input_dict['datasets']

        for templatetype in self.input_dict['template']['templatetypes']:
            key = self.type_to_class_conversion[templatetype.resource_type]
            self.parsed_template[key].append(templatetype)

        return self.parsed_template


    def export_components(self, overwrite=False):
        """Export the template to a set of pynsim agent classes."""
        env = Environment(loader=FileSystemLoader(self.basepath + os.sep
                                                  + 'template'))
        template = env.get_template('agenttemplate.py')

        for typ, resources in self.parsed_template.items():
            outfile = self.output + os.path.sep + "%ss.py" % typ.lower()
            print("Writing file %s ..." % outfile)
            with open(outfile, 'w') as f:
                f.write(template.render(agent_type=typ,
                                        resources=resources,
                                       attr_lookup = self.attr_lookup))


def commandline_parser():
    parser = ap.ArgumentParser(prog='Hydra2pynsim.py', description="""
Convert a HydraPlatform template to a set of pynsim agent classes.

(c) Copyright 2015
Eawag: Swiss Federal Institute of Aquatic Science and Technology
""", formatter_class=ap.RawDescriptionHelpFormatter)

    parser.add_argument('-t', '--template',
                        help="A template ID, template name or the path to a template JSON file")
    parser.add_argument('-o', '--output',
                        help="Name of the folder where files will be created.")
    parser.add_argument('-x', '--overwrite', action='store_true',
                        help="Overwrite existing folder.")

    return parser

if __name__ == '__main__':
    parser = commandline_parser()
    args = parser.parse_args()
    print(args)
    converter = HydraTemplateToPynsim(input_template=args.template,
                                        output=args.output)
    converter.load_template()
    converter.parse_template()
    converter.export_components(overwrite=args.overwrite)
