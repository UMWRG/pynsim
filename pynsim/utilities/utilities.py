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
import importlib

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

class Utilities:
    def __init__(self):
        pass

    def get_time_steps(self, data_file_name ):
        """
            Gets the timesteps reading the file
        """
        with open(data_file_name) as json_file:
            data = json.load(json_file)
            if "timestepper" not in data:
                raise Exception("No timestepper in the file")
            else:
                if "range" in data["timestepper"]:
                    min=0
                    max=0
                    if "min" in data["timestepper"]["range"]:
                        min = data["timestepper"]["range"]["min"]
                    if "max" in data["timestepper"]["range"]:
                        max = data["timestepper"]["range"]["max"]
                    return range(min,max)
                else:
                    raise Exception("No known timestepper in the file!")


    def create_components(self, simulation, simulation_components, data_file_name, classes_array):
        """
            Create components getting data from a json file
        """
        with open(data_file_name) as json_file:
            data = json.load(json_file)
            if "nodes" not in data:
                raise Exception("No nodes in the file")
            elif "links" not in data:
                raise Exception("No links in the file")
            else:
                # Looks Nodes to instance
                nodes_list = data["nodes"]
                for comp_data in nodes_list:
                    comp_name = comp_data["name"]
                    comp_type = comp_data["type"]
                    if comp_name in simulation_components:
                        raise Exception(f"Component '{comp_name}' already defined!")
                    else:
                        for class_in_array in classes_array["nodes"]:
                            if comp_data["type"] == class_in_array.get_class_name():

                                new_node = class_in_array(simulator=simulation, x=comp_data["x"], y=comp_data["y"], name=comp_data["name"])
                                simulation_components[comp_name] = new_node
                                simulation.network.add_node(new_node)
                                break
                        else:
                            raise Exception(f"Component type '{comp_type}' not valid!")

                # Looks Links to instance
                links_list = data["links"]
                for comp_data in links_list:
                    comp_name = comp_data["name"]
                    comp_type = comp_data["type"]
                    if comp_name in simulation_components:
                        raise Exception(f"Component '{comp_name}' already defined!")
                    else:
                        for class_in_array in classes_array["links"]:
                            if comp_data["type"] == class_in_array.get_class_name():

                                new_link = class_in_array(
                                    simulator=simulation,
                                    start_node=simulation_components[comp_data["start_node"]],
                                    end_node=simulation_components[comp_data["end_node"]],
                                    name=comp_data["name"]
                                )
                                simulation_components[comp_name] = new_link
                                simulation.network.add_link(new_link)
                                break
                        else:
                            raise Exception(f"Component type '{comp_type}' not valid!")


    def update_components_from_file(self,simulation_components, data_file_name):
        """
            Passing an array of components, it setups them using data in file_path
        """
        with open(data_file_name) as json_file:
            data = json.load(json_file)
            if "nodes" not in data:
                raise Exception("No nodes in the file")
            elif "links" not in data:
                raise Exception("No links in the file")
            else:
                nodes_list = data["nodes"]
                for comp_data in nodes_list:
                    self.update_single_component(simulation_components, comp_data)
                links_list = data["links"]
                for comp_data in links_list:
                    self.update_single_component(simulation_components, comp_data)

    def update_single_component(self, simulation_components, comp_data):
        """
            Updates a single component
        """
        if "properties" in comp_data:
            comp_name = comp_data["name"]
            if comp_name in simulation_components:
                props_evaluated={}
                while True:
                    props_to_evaluate={}

                    for prop_name in comp_data["properties"]:
                        # Copy the props to evaluate
                        if prop_name not in props_evaluated:
                            props_to_evaluate[prop_name]=deepcopy(comp_data["properties"][prop_name])

                    if len(props_to_evaluate) == 0:
                        # Finished full props evaluation
                        break

                    for prop_name in props_to_evaluate:
                        val = props_to_evaluate[prop_name]

                        m = re.search('\{\{([^}]*)\}\}', str(val))

                        property_fully_evaluated = True
                        new_expression=[]

                        if m is not None:
                            # The property contains an expression. Trying to evaluate it
                            expression = m.group(1).strip()
                            new_built_expression=expression

                            last_position = 0
                            for m in re.finditer(r"(self\.([a-zA-Z_.]+))", expression):
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
                            setattr(simulation_components[comp_name], prop_name, val)
                            props_evaluated[prop_name] = val
