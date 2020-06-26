import logging
import time
from copy import deepcopy, copy
import jsonpickle
import json

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

from .property_status import PropertyStatus


class ComponentStatus(object):
    """
        This class models the status of an object, indexed by:
            - property_name
            - scenario_tuple
            - timestep

        [property_name][scenario_tuple][timestep]

    """

    def __init__(self, component_ref=None, properties={}):
        self._component_ref = component_ref
        self._save_components_history = component_ref.get_simulator().get_save_components_history_flag()
        self._status = {
            # This represents the current index of the scenario.
            # This is necessary to select the current item
            "current_multiscenario_index": {
                "tuple": None,
                "array": None
            },

            "current_timestep": None,

            # This represents the status of the compoente
            "properties": properties
        }
        for property_name in self._status["properties"]:
            self.init_property_object(property_name)


    def __repr__(self):
        return jsonpickle.encode({
            "status": self._status
        })

    def init_property_object(self, name):
        """
            In case that the property object is not properly defined, it defines it
        """
        if name not in self._status["properties"]:
            # The property is missing
            self._status["properties"][name] = PropertyStatus(component_ref=self._component_ref, name=name, save_components_history = self._save_components_history)
        if not isinstance(self._status["properties"][name], PropertyStatus):
            # The property value is not a proper class
            current_value = deepcopy(self._status["properties"][name])
            self._status["properties"][name] = PropertyStatus(component_ref=self._component_ref, name=name, save_components_history = self._save_components_history)
            if current_value is not None:
                self.set_property_value(name, current_value)

    def set_property_start_value(self, name, value):
        """
            Setting the component property start value
        """
        self.init_property_object(name)
        self._status["properties"][name].set_start_value(value)

    def set_property_value(self, name, value):
        """
            Set a property value using the current value
        """
        self.init_property_object(name)
        self._status["properties"][name].set_value(value)

    def get_property_current_value(self, name):
        self.init_property_object(name)

        return self._status["properties"][name].get_current_value()

    def get_property_previous_value(self, name):
        self.init_property_object(name)

        return self._status["properties"][name].get_previous_value()

    def set_current_timestep(self, current_timestep):
        """
            Sets current timestep
        """
        self._status["current_timestep"] = current_timestep
        for property in self._status["properties"]:
            self._status["properties"][property].set_current_timestep(current_timestep)

    def get_current_scenario_index_tuple(self):
        """
            Gets current scenario tuple
        """
        return self._status["current_multiscenario_index"]["tuple"]

    def get_current_timestep(self):
        """
            Gets current timestep
        """
        return self._status["current_timestep"]

    def set_current_scenario_index_tuple(self, current_multiscenario_index_tuple):
        """
            Sets current scenario tuple and array starting from tuple
        """
        self._status["current_multiscenario_index"]["tuple"] = current_multiscenario_index_tuple
        self._status["current_multiscenario_index"]["array"] = current_multiscenario_index_tuple.split(",")

        for property in self._status["properties"]:
            self._status["properties"][property].set_index_tuple(current_multiscenario_index_tuple)

    def set_current_scenario_index_array(self, current_multiscenario_index_array):
        """
            Sets current scenario tuple and array starting from array
        """
        self._status["current_multiscenario_index"]["array"] = current_multiscenario_index_array
        self._status["current_multiscenario_index"]["tuple"] = ",".join(current_multiscenario_index_array)

    def __repr__(self):
        """
            Dumps the status as an array of properties
        """
        output = {
            "properties": []
        }

        for property_name in self._status["properties"]:
            output["properties"].append(json.loads(repr(self._status["properties"][property_name])))

        return repr(output)

    def get_full_status(self):
        """
            Dumps the status as an array of properties
        """
        output = {
            "properties": []
        }

        for property_name in self._status["properties"]:
            output["properties"].append(self._status["properties"][property_name].get_status())

        return output
