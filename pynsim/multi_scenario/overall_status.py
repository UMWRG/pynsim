"""
    This object mantain the status of all the properties of all the components of the simulation
"""
import types
import array

import numpy as np
import logging
import json

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

"""
    the status has the following indexing
    component_name, property_name, scenario_index, timestep_value
"""
class OverallStatus(object):
    def __init__(self, save_components_history=True):
        """
            Component Initialization
        """
        self.status = {}
        self.timesteps = []

        self.last_shown_history_json = ""

        self.defined_scenarios_list = []

        # Indexed by scenario tuple returns the index of the "defined_scenarios_list" array
        self.defined_scenarios_mappings = dict()

    def set_value(self, component_name, property_name, scenario_index, timestep_value, property_value):
        """
            Method used to set the value of the item identified by the tuple:
            (component_name, property_name, scenario_index, timestep_value)
        """
        if timestep_value is not None and timestep_value not in self.timesteps:
            self.timesteps.append(timestep_value)
        if scenario_index is None and timestep_value is None and property_value is None:
            return
        if component_name  not in self.status:
            self.status[component_name] = {}
        if property_name  not in self.status[component_name]:
            self.status[component_name][property_name] = {}
        if scenario_index is None:
            self.status[component_name][property_name]["_default_"] = property_value
        else:
            if scenario_index not in self.defined_scenarios_list:
                self.defined_scenarios_mappings[scenario_index] = len(self.defined_scenarios_list)
                self.defined_scenarios_list.append(scenario_index)


            if scenario_index not in self.status[component_name][property_name]:
                self.status[component_name][property_name][scenario_index] = {}
            if timestep_value not in self.status[component_name][property_name][scenario_index]:
                self.status[component_name][property_name][scenario_index][timestep_value] = None

            self.status[component_name][property_name][scenario_index][timestep_value] = property_value

    def get_value(self, component_name, property_name, scenario_index, timestep_value):
        """
            Method used to return_array the value of the item identified by the tuple:
            (component_name, property_name, scenario_index, timestep_value)
        """
        return_value=None

        if component_name  not in self.status:
            return_value = None
        elif property_name  not in self.status[component_name]:
            return_value = None
        elif scenario_index is None:
            return_value = self.status[component_name][property_name]["_default_"]
        else:
            if scenario_index not in self.status[component_name][property_name]:
                try:
                    return_value = self.status[component_name][property_name]["_default_"]
                except Exception:
                    logger.warning(self.dump())
                    raise Exception("Stop get_value 1")
            elif timestep_value not in self.status[component_name][property_name][scenario_index]:
                try:
                    return_value = self.status[component_name][property_name]["_default_"]
                except Exception:
                    logger.warning(self.dump())
                    raise Exception("Stop get_value 2")
            else:
                return_value = self.status[component_name][property_name][scenario_index][timestep_value]

        return return_value


    def get_property_history(self, component_name, property_name, scenario_index):
        """
            Returns the full history of a tuple (component, property, scenario_index)
        """

        if component_name  not in self.status:
            return_value = None
        elif property_name  not in self.status[component_name]:
            return_value = None
        elif scenario_index is None:
            return_value = self.status[component_name][property_name]["_default_"]
        else:
            if scenario_index not in self.status[component_name][property_name]:
                """
                    For current property the scenario has not been still defined!
                """
                try:
                    if "_default_" in self.status[component_name][property_name]:
                        return_value = self.status[component_name][property_name]["_default_"]
                    else:
                        return_value = []
                except Exception:
                    logger.warning(self.dump())
                    logger.warning("scenario_index {} component_name {} property_name {}".format(scenario_index, component_name, property_name))
                    raise Exception("Stop get_property_history 1")

            else:
                return_value = self.status[component_name][property_name][scenario_index]

        return return_value

    def get_property_history_as_array(self, component_name, property_name, scenario_index):
        """
            Returns the history of a property of a component as array
        """
        return_array = []
        history_dict = self.get_property_history(component_name, property_name, scenario_index)

        if isinstance(history_dict, dict) or isinstance(history_dict, list):
            for item in history_dict:
                attr = history_dict[item]
                if isinstance(attr, dict) or isinstance(attr, list):
                    return_array.append(deepcopy(attr))
                else:
                    return_array.append(attr)
        else:
            for timestep in self.timesteps:
                return_array.append(history_dict)

        return return_array

    def get_component_history_as_dict(self, component_name, scenario_index, properties_allowed=None):
        """
            Returns the history of all properties of a component as dict of arrays
        """
        return_dict = dict()
        if component_name in self.status:
            for property_name in self.status[component_name]:
                if properties_allowed is None or property_name in properties_allowed:
                    return_dict[property_name] = self.get_property_history_as_array(component_name, property_name, scenario_index)

        return return_dict

    def get_scenarios_count(self):
        """
            Returns the length of the list of defined scenarios
        """
        return len(self.defined_scenarios_list)

    def get_scenarios_list(self):
        """
            Returns the list of defined scenarios
        """
        return self.defined_scenarios_list

    def dump(self):
        """
            Return the full status
        """
        return json.dumps(self.status)

    def get_scenarios_indexes_list(self):
        """
            Returns all the defined scenario indexes
        """
        return self.defined_scenarios_list

    def export_status_indexed_by_scenarios(self):
        """
            Exports the status indexing it :
            - "constants" | "scenarios"
            for "scenarios" items
            - <scenario id (num)>
            - "index" | "timesteps"
            for "timesteps" items
            - <timestep>
            - <component name>
            - <property name>
        """
        export_data = dict()
        for component_name in self.status:
            component_status = self.status[component_name]
            for property_name in component_status:
                property_status = component_status[property_name]
                for scenario_index in property_status:
                    if scenario_index == "_default_":
                        # Just one value
                        if "constants" not in export_data:
                            export_data["constants"] = dict()

                        if component_name not in export_data["constants"]:
                            export_data["constants"][component_name] = dict()

                        export_data["constants"][component_name][property_name] = property_status[scenario_index]
                    else:
                        # It is a scenario index
                        if "scenarios" not in export_data:
                            export_data["scenarios"] = dict()

                        scenario_serial_id = str(self.defined_scenarios_mappings[scenario_index])
                        if scenario_serial_id not in export_data["scenarios"]:
                            export_data["scenarios"][scenario_serial_id] = dict()
                            export_data["scenarios"][scenario_serial_id]["index"] =scenario_index
                            export_data["scenarios"][scenario_serial_id]["timesteps"] = dict()

                        scenario_values = property_status[scenario_index]
                        for timestep_key in scenario_values:
                            timestep_value = scenario_values[timestep_key]

                            if timestep_key not in export_data["scenarios"][scenario_serial_id]["timesteps"]:
                                export_data["scenarios"][scenario_serial_id]["timesteps"][timestep_key] = dict()

                            if component_name not in export_data["scenarios"][scenario_serial_id]["timesteps"][timestep_key]:
                                export_data["scenarios"][scenario_serial_id]["timesteps"][timestep_key][component_name] = dict()

                            export_data["scenarios"][scenario_serial_id]["timesteps"][timestep_key][component_name][property_name] = timestep_value

        return export_data
