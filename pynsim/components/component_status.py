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
            - scenario_id
            - timestep

        [property_name][scenario_id][timestep]

    """

    def __init__(self, component_ref=None):
        self._component_ref = component_ref
        self._save_components_history = component_ref.get_simulator().get_save_components_history_flag()
        self._status = {
            # This represents the current index of the scenario.
            # This is necessary to select the current item
            "current_multiscenario_index": {
                "scenario_id": None,
                "array": None
            },

            "current_timestep": None
        }
        self.current_scenario_id_mandatory_flag = False

    def __repr__(self):
        return jsonpickle.encode({
            "status": self._status
        })

    def set_current_timestep(self, current_timestep):
        """
            Sets current timestep
        """
        self._status["current_timestep"] = current_timestep


    def set_current_scenario_id_mandatory_flag(self):
        """
            To set a flag to eventually make mandatory the scenario_id settings
            IF:
                True => the component raises an exception if scenario_id is found None in any operation
                False => the component temporary allows scenario_id being None in any operation
        """
        self.current_scenario_id_mandatory_flag = True


    def get_current_scenario_id(self):
        """
            Gets current scenario id.
            Fails if the scenario id has not been set after the simulation finished and the data has to be returned
        """
        if self.current_scenario_id_mandatory_flag is True and self._status["current_multiscenario_index"]["scenario_id"] is None:
            # The simulation is finished and data is ready.
            # Therefore setting scenario id is mandatory!
            raise Exception("To get data from the component you must set the scenario ID!")
        return self._status["current_multiscenario_index"]["scenario_id"]

    def get_current_timestep(self):
        """
            Gets current timestep
        """
        return self._status["current_timestep"]

    def set_current_scenario_id(self, current_scenario_id):
        """
            Sets current scenario scenario_id and array starting from tuple
        """
        self._status["current_multiscenario_index"]["scenario_id"] = current_scenario_id
        self._status["current_multiscenario_index"]["array"] = current_scenario_id.split(",")

    def reset_current_scenario_id(self):
        """
            Resets the current scenario ID.
        """
        self._status["current_multiscenario_index"]["scenario_id"] = None
        self._status["current_multiscenario_index"]["array"] = None

    def set_current_scenario_index_array(self, current_multiscenario_index_array):
        """
            Sets current scenario scenario_id and array starting from array
        """
        self._status["current_multiscenario_index"]["array"] = current_multiscenario_index_array
        self._status["current_multiscenario_index"]["scenario_id"] = ",".join(current_multiscenario_index_array)
