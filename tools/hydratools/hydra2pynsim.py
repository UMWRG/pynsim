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
from lxml import etree

import argparse as ap


class HydraTemplateTopynsim(object):

    _type_to_class_conversion = dict(NODE='Node',
                                     LINK='Link',
                                     NETWORK='Network',
                                     GROUP='Institution',
                                     )

    def __init__(self, input_file, output=None):
        self.input_file = os.path.abspath(os.path.expanduser(input_file))
        if output is None:
            self.output, ext = os.path.splitext(self.inputfile)
        else:
            self.output = os.path.abspath(os.path.expanduser(output))

        self.template_root = None
        self.templatedict = dict(Node=[], Link=[], Institution=[], Network=[])
        self.basepath = os.path.dirname(os.path.abspath(__file__))

    def load_template(self):
        """Load and validate the HydraPlatform template XML."""
        schema_root = etree.parse(self.basepath + os.sep
                                  + 'xml' + os.sep + 'template.xsd')
        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)
        self.template_root = etree.parse(self.input_file, parser=parser)

    def parse_template(self):
        """Convert the template to dictionary."""

        if not os.path.exists(self.output):
            os.makedirs(self.output)
        print 'Files written to: ' + self.output

        for element in self.template_root.iter("resource"):
            resourcedict = dict(attributes=[])
            for child in element.getchildren():
                if child.tag == 'type':
                    type = self._type_to_class_conversion[child.text]
                elif child.tag == 'name':
                    type_name = child.text
                    resourcedict['type_name'] = type_name
                    type_name = type_name.title()
                    type_name = re.sub('[^0-9a-zA-Z]+', '', type_name)
                    resourcedict['class_name'] = type_name
                elif child.tag == 'attribute':
                    if child.find('default') is None:
                        default_value = None
                    else:
                        default = child.find('default')
                        data_type = child.find('data_type')
                        default_value = default.find('value').text
                        if data_type is None:
                            try:
                                default_value = float(default_value)
                            except ValueError:
                                pass
                        elif data_type.text == 'scalar':
                            default_value = float(default_value)
                    attrdict = dict(name=child.find('name').text,
                                    value=default_value)
                    resourcedict['attributes'].append(attrdict)
            self.templatedict[type].append(resourcedict)

    def export_components(self, overwrite=False):
        """Export the template to a set of pynsim agent classes."""
        env = Environment(loader=FileSystemLoader(self.basepath + os.sep
                                                  + 'template'))
        template = env.get_template('agenttemplate.py')

        for typ, resources in self.templatedict.iteritems():
            if resources:
                outfile = self.output + os.path.sep + "%ss.py" % typ.lower()
                print "Writing file %s ..." % outfile
                with open(outfile, 'w') as f:
                    f.write(template.render(agent_type=typ,
                                            resources=resources))


def commandline_parser():
    parser = ap.ArgumentParser(prog='Hydra2pynsim.py', description="""
Convert a HydraPlatform template to a set of pynsim agent classes.

(c) Copyright 2015
Eawag: Swiss Federal Institute of Aquatic Science and Technology
""", formatter_class=ap.RawDescriptionHelpFormatter)

    parser.add_argument('file', metavar='FILE',
                        help="XML file of the pynsim model")
    parser.add_argument('-o', '--output',
                        help="Name of the folder where files will be created.")
    parser.add_argument('-x', '--overwrite', action='store_true',
                        help="Overwrite existing folder.")

    return parser

if __name__ == '__main__':
    parser = commandline_parser()
    args = parser.parse_args()
    converter = HydraTemplateTopynsim(input_file=args.file,
                                        output=args.output)
    converter.load_template()
    converter.parse_template()
    converter.export_components(overwrite=args.overwrite)
