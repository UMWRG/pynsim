#    (c) Copyright 2014, University of Manchester
#
#    This file is part of PyNSim.
#
#    PyNSim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNSim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNSim.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time
import json
from datetime import datetime
import os
from copy import deepcopy
import re

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

class Utilities:
    def __init__(self):
        pass

    def update_components_from_file(self,simulation_components, data_file_name):
        """
            Passing an array of components, it setups them using data in file_path
        """
        with open(data_file_name) as json_file:
            data = json.load(json_file)
            for comp_name in data:
                if comp_name in simulation_components:
                    props_evaluated={}
                    cno=0
                    while True:
                        cno=cno+1
                        # print("----------------------------------------------------------")
                        # print(f"Start Cycle number {cno}")
                        # print("----------------------------------------------------------")
                        # input("")
                        props_to_evaluate={}
                        for prop_name in data[comp_name]:
                            # Copy the props to evaluate
                            if prop_name not in props_evaluated:
                                props_to_evaluate[prop_name]=deepcopy(data[comp_name][prop_name])

                        if len(props_to_evaluate) == 0:
                            # Finished full props evaluation
                            break

                        for prop_name in props_to_evaluate:
                            # print("Property name: %s", prop_name)
                            val = props_to_evaluate[prop_name]
                            # print("Property value: %s", val)

                            m = re.search('\{\{([^}]*)\}\}', str(val))

                            property_fully_evaluated = True
                            new_expression=[]

                            if m is not None:
                                # The property contains an expression. Trying to evaluate it
                                # print(m.group(1))
                                expression = m.group(1).strip()
                                # print(expression)
                                new_built_expression=expression

                                last_position = 0
                                for m in re.finditer(r"(self\.([a-zA-Z_.]+))", expression):
                                    # print( '%02d-%02d: %s : %s' % (m.start(), m.end(), m.group(1), m.group(2)))
                                    depending_var_name = m.group(2)

                                    if depending_var_name not in props_evaluated:
                                        property_fully_evaluated = False
                                        break

                                    prefix=""
                                    postfix=""
                                    if m.start() > 0:
                                        prefix = expression[last_position:m.start()-1]

                                    last_position = m.end() + 1

                                    new_expression.append(prefix)
                                    new_expression.append(props_evaluated[depending_var_name])

                                if m.end() < len(expression) - 1 and property_fully_evaluated is True:
                                    new_expression.append(expression[m.end()+1:])

                                if property_fully_evaluated is True:
                                    full_expression = " ".join((str(x) for x in new_expression))
                                    val = eval(full_expression)


                            if property_fully_evaluated is True:
                                # print("Evaluate")
                                # print(f"{prop_name} = {val}")
                                setattr(simulation_components[comp_name], prop_name, val)
                                props_evaluated[prop_name] = val
                            # else:
                            #     print("NOT Evaluate")
                            # print("==================")
