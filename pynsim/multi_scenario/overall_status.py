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
        self.status = {}
        self.timesteps = []

        self.last_shown_history_json = ""

    def set_value(self, component_name, property_name, scenario_index, timestep_value, property_value):
        # logger.warning("OverallStatus.set_value: {} - {} - {} - {} - {}".format(component_name, property_name, scenario_index, timestep_value, property_value))
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
            if scenario_index not in self.status[component_name][property_name]:
                self.status[component_name][property_name][scenario_index] = {}
            if timestep_value not in self.status[component_name][property_name][scenario_index]:
                self.status[component_name][property_name][scenario_index][timestep_value] = None

            self.status[component_name][property_name][scenario_index][timestep_value] = property_value

        #input("OVERALL")

    def get_value(self, component_name, property_name, scenario_index, timestep_value):
        # logger.warning(f"{component_name}-{property_name}-{scenario_index}-{timestep_value}")
        return_value=None
        # if property_name == "init_stor":
        #     input("Ci siamo")
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

        # logger.warning(f"Return value: {return_value}")
        # if property_name == "init_stor":
        #     input("LEGGI")
        return return_value


    def get_property_history(self, component_name, property_name, scenario_index):
        """
            Returns the full history of a tuple (component, property, scenario_index)
        """
        if self.last_shown_history_json != json.dumps(self.status):
            self.last_shown_history_json = json.dumps(self.status)
            print(self.status)
            # input("^^^^^^^^ Current Full History ^^^^^^^^^^^^")


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
            Returns the history of a property of a component
        """
        return_array = []
        history_dict = self.get_property_history(component_name, property_name, scenario_index)

        print(f"self.get_property_history('{component_name}', '{property_name}', '{scenario_index}')")
        print(history_dict)
        # print(self.timesteps)
        #if property_name == "S":
            # input("^^^^^^^^^ get_property_history_as_array ^^^^^^^^^")

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

    def get_component_history_as_dict(self, component_name, scenario_index):
        """
            Returns the history of all properties of a component
        """
        return_dict = dict()
        if component_name in self.status:
            for property_name in self.status[component_name]:
                return_dict[property_name] = self.get_property_history_as_array(component_name, property_name, scenario_index)

        return return_dict


    def dump(self):
        return self.status
