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
import imp
import glob
import inspect
from lxml import etree

import argparse as ap

import sys

from pynsim.components import Node
from pynsim.components import Link
from pynsim.components import Network
from pynsim.components import Institution

global __location__
__location__ = os.path.realpath(os.path.split(sys.argv[0])[0])


class PynsimToHydraTemplate(object):

    def __init__(self, folder=None, output=None, name=None):
        self.folder = os.path.abspath(os.path.expanduser(folder))
        if output is None:
            output = self.folder
            while len(os.path.split(output)[-1]) == 0:
                output = os.path.split(output)[-2]
            self.output = os.path.split(output)[-1] + '.xml'
        else:
            self.output = output

        self.tree = etree.Element('template_definition')
        if name is None:
            self.template_name = 'HydraPlatform template for %s' % \
                            self.output.split('.')[0]
        else:
            self.template_name = name

        tname = etree.SubElement(self.tree, 'template_name')
        tname.text = self.template_name

        self.resource_dict = {'NETWORK':[], 'NODE':[], 'LINK':[], 'GROUP':[]}


    def build_hm_grouping_xml(self):
        layout = etree.SubElement(self.tree, 'layout')
        item = etree.SubElement(layout, 'item')
        name = etree.SubElement(item, 'name')
        name.text = 'grouping'
        value = etree.SubElement(item, 'value')

        name2 = etree.SubElement(value, 'name')
        name2.text = self.template_name

        description = etree.SubElement(value, 'description')
        description.text = "An automatically generated template using pynsim2hydra."

        cats = etree.SubElement(value, 'categories')
        for k, modules in self.resource_dict.items():
            if k in ('NETWORK', 'GROUP'):
                continue

            duplicate_modules = []
            if len(modules) > 0:
                cat  = etree.SubElement(cats, 'category')
                catname  = etree.SubElement(cat, 'name')
                catname.text = k
                catdesc  = etree.SubElement(cat, 'description')
                catdesc.text = '%s Resources'%(k.lower())
                catdispname  = etree.SubElement(cat, 'displayname')
                catdispname.text ='%s Resources'%(k.lower())

                groups = etree.SubElement(cat, 'groups')

                for module in modules:
                    if module[0] in duplicate_modules:
                        continue
                    else:
                        duplicate_modules.append(module[0])


                    grp = etree.SubElement(groups, 'group')
                    grpname  = etree.SubElement(grp, 'name')
                    grpname.text = module[0]
                    grpdesc  = etree.SubElement(grp, 'description')
                    grpdesc.text = module[0]
                    grpdispname  = etree.SubElement(grp, 'displayname')
                    grpdispname.text = module[0]
                    grpdispname  = etree.SubElement(grp, 'image')
                    grpdispname.text = ''

    def build_xml_body(self):
        #print mb[1]

        ress = etree.SubElement(self.tree, 'resources')
        for resource_type, modules in self.resource_dict.items():
            duplicate_modules = []
            if len(modules) > 0:
                for module in modules:
                    if module[0] in duplicate_modules:
                        continue
                    else:
                        duplicate_modules.append(module[0])
                    res = etree.SubElement(ress, 'resource')
                    typ = etree.SubElement(res, 'type')
                    typ.text = resource_type
                    #print typt
                    name = etree.SubElement(res, 'name')
                    name.text = module[0]


                    if resource_type not in ('NETWORK', 'GROUP'):
                        layout = etree.SubElement(res, 'layout')

                        #Stuff needed for HM
                        grpitem = etree.SubElement(layout, 'item')
                        grpname = etree.SubElement(grpitem, 'name')
                        grpname.text = 'group'
                        grpval = etree.SubElement(grpitem, 'value')
                        grpval.text = module[0]


                        if hasattr(module[1], 'colour'):

                            colour = module[1].colour
                        else:
                            colour = 'black'

                        colouritem = etree.SubElement(layout, 'item')
                        colourname = etree.SubElement(colouritem, 'name')
                        colourname.text = 'colour'
                        colourval = etree.SubElement(colouritem, 'value')
                        colourval.text = colour

                        if resource_type == 'NODE':
                            shapeitem = etree.SubElement(layout, 'item')
                            shapename = etree.SubElement(shapeitem, 'name')
                            shapename.text = 'symbol'
                            shapeval = etree.SubElement(shapeitem, 'value')
                            shapeval.text = 'circle'

                        if resource_type == 'LINK':
                            shapeitem = etree.SubElement(layout, 'item')
                            shapename = etree.SubElement(shapeitem, 'name')
                            shapename.text = 'symbol'
                            shapeval = etree.SubElement(shapeitem, 'value')
                            shapeval.text = 'solid'

                            weightitem = etree.SubElement(layout, 'item')
                            weightname = etree.SubElement(weightitem, 'name')
                            weightname.text = 'line_weight'
                            weightval = etree.SubElement(weightitem, 'value')
                            weightval.text = '1'


                    attdic = module[1]._properties
                    #print attdic
                    for i in range(len(attdic)):
                        att = etree.SubElement(res, 'attribute')
                        att_name = etree.SubElement(att, 'name')
                        att_name.text = attdic.keys()[i]
                        att_dim = etree.SubElement(att, 'dimension')
                        att_dim.text="dimensionless"
                        att_var = etree.SubElement(att, 'is_var')
                        att_var.text = 'N'
                        data_type = etree.SubElement(att, 'data_type')
                        data_type.text = 'scalar'

    def convert(self):
        self.get_modules()
        self.build_hm_grouping_xml()
        self.build_xml_body()
        self.write_output()
        self.check_template()

    def get_modules(self):
        listd = os.listdir(self.folder)

        os.chdir(self.folder)
        sys.path.append(self.folder)

        for dir in listd:
            if os.path.isdir(self.folder + os.path.sep + dir):
                sys.path.append(self.folder + os.path.sep + dir)
                listf = glob.glob(self.folder + os.path.sep + dir + os.path.sep
                                  + '*.py')

                for file in listf:
                    fname = os.path.split(file)[-1]
                    if fname[0] == '_':
                        continue
                    fname = "%s.%s"%(dir, fname[0:-3])
                    print "\nloading %s, (%s)\n"%(fname, file)
                    #print fname, file

                    try:
                        mod = imp.load_source(fname, file)
                    except ImportError, e:
                        print e
                        continue
                    #print(mod)
                    for mb in inspect.getmembers(mod):
                        if inspect.isclass(mb[1]) and mb[0] != 'Link' \
                           and mb[0] != 'Network' and mb[0] != 'Node' \
                           and mb[0] != 'Institution':
                            if issubclass(mb[1], Node):
                                typt = 'NODE'
                            elif issubclass(mb[1], Link):
                                typt = 'LINK'
                            elif issubclass(mb[1], Network):
                                typt = 'NETWORK'
                            elif issubclass(mb[1], Institution):
                                typt = 'GROUP'
                            else:
                                continue
                            self.resource_dict[typt].append(mb)
                    #print ''

        os.chdir(__location__)

    def write_output(self):
        with open(self.output, "w") as fout:
            fout.write(etree.tostring(self.tree, pretty_print=True))


    def check_template(self):
        """Load and validate the HydraPlatform template XML."""

        path_to_xsd = "%s%sxml%stemplate.xsd"%(__location__,os.sep,os.sep)

        print path_to_xsd

        schema_root = etree.parse(path_to_xsd)
        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)
        self.template_root = etree.parse(self.output, parser=parser)


def commandline_parser():
    parser = ap.ArgumentParser(prog='pynsim2hydra.py', description="""
Convert a set of pynsim agent classes to a HydraPlatform template.

(c) Copyright 2015
Eawag: Swiss Federal Institute of Aquatic Science and Technology
""", formatter_class=ap.RawDescriptionHelpFormatter)

    parser.add_argument('folder', metavar='FOLDER',
                        help="Main folder of the pynsim model")
    parser.add_argument('-o', '--output',
                        help="(Optional) Filename of the template created.")
    parser.add_argument('-n', '--template-name',
                        help="(Optional) Name of the template..")

    return parser

if __name__ == '__main__':
    parser = commandline_parser()
    args = parser.parse_args()
    converter = PynsimToHydraTemplate(folder=args.folder, output=args.output,
                                     name=args.template_name)
    converter.convert()
