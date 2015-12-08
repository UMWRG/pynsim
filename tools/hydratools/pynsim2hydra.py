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

from pynsim.components import Node
from pynsim.components import Link
from pynsim.components import Network
from pynsim.components import Institution


class PynsimToHydraTemplate(object):

    def __init__(self, folder=None, output=None):
        self.folder = os.path.abspath(os.path.expanduser(folder))
        if output is None:
            output = self.folder
            while len(os.path.split(output)[-1]) == 0:
                output = os.path.split(output)[-2]
            self.output = os.path.split(output)[-1] + '.xml'
        else:
            self.output = output

    def convert(self):

        tree = etree.Element('template_definition')
        tname = etree.SubElement(tree, 'template_name')
        tname.text = 'HydraPlatform template for %s' % \
            self.output.split('.')[0]
        ress = etree.SubElement(tree, 'resources')

        listd = os.listdir(self.folder)

        for dir in listd:
            if os.path.isdir(self.folder + os.path.sep + dir):

                listf = glob.glob(self.folder + os.path.sep + dir + os.path.sep
                                  + '*.py')

                for file in listf:
                    fname = os.path.split(file)[-1]
                    if fname[0] == '_':
                        continue
                    fname = fname[0:-3]
                    #print fname, file
                    mod = imp.load_source(fname, file)
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
                                typt = 'INSTITUTION'
                            else:
                                continue
                            #print mb[1]
                            res = etree.SubElement(ress, 'resource')
                            typ = etree.SubElement(res, 'type')
                            typ.text = typt
                            #print typt
                            name = etree.SubElement(res, 'name')
                            name.text = mb[0]
                            attdic = mb[1]._properties
                            #print attdic
                            for i in range(len(attdic)):
                                att = etree.SubElement(res, 'attribute')
                                att_name = etree.SubElement(att, 'name')
                                att_name.text = attdic.keys()[i]
                                att_dim = etree.SubElement(att, 'dimension')
                                att_var = etree.SubElement(att, 'is_var')
                                att_var.text = 'N'
                    #print ''

        with open(self.output, "w") as fout:
            fout.write(etree.tostring(tree, pretty_print=True,
                                      xml_declaration=True, encoding='utf-8'))


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

    return parser

if __name__ == '__main__':
    parser = commandline_parser()
    args = parser.parse_args()
    converter = PynsimToHydraTemplate(folder=args.folder)
    converter.convert()
