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

class ComponentStatus(object):
    """
        This class models the status of an object, indexed by:
            - property_name
            - scenario_tuple
            - timestep

        [property_name][scenario_tuple][timestep]

    """

    def __init__(self, component_ref=None):
        self._component_ref = component_ref
        self._save_components_history = component_ref.get_simulator().get_save_components_history_flag()
        self._status = {
            # This represents the current index of the scenario.
            # This is necessary to select the current item
            "current_multiscenario_index": {
                "tuple": None,
                "array": None
            },

            "current_timestep": None
        }

    def __repr__(self):
        return jsonpickle.encode({
            "status": self._status
        })

    def set_current_timestep(self, current_timestep):
        """
            Sets current timestep
        """
        self._status["current_timestep"] = current_timestep

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

    def set_current_scenario_index_array(self, current_multiscenario_index_array):
        """
            Sets current scenario tuple and array starting from array
        """
        self._status["current_multiscenario_index"]["array"] = current_multiscenario_index_array
        self._status["current_multiscenario_index"]["tuple"] = ",".join(current_multiscenario_index_array)
