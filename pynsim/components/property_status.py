import logging
import types
from copy import deepcopy, copy
import json
import jsonpickle
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)


class PropertyStatus(object):
    """
        This class models the status of an object, indexed by:
            - timestep
            - scenario_tuple

        obj[timestep][scenario_tuple]
    """
    def __init__(self, component_ref=None, name=None, save_components_history = True):
        self._component_ref = component_ref
        self.name = name
        self._save_components_history = save_components_history
        self._status = types.SimpleNamespace()

        self._status.current_index_tuple = None
        self._status.current_timestep = None
        self._status.start_value = None
        self._status.history = {}
        self._timesteps = []

    def __repr__(self):
        repr={
            "name": self.name,
            "save_components_history": self._save_components_history,
            "status": self._status
        }
        return json.dumps(
            repr,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=2
        )

    def get_status(self):
        repr={
            "name": self.name,
            "save_components_history": self._save_components_history,
            "status": self._status
        }
        return repr



    def set_current_timestep(self, timestep):
        """
            Set the current timestep
        """
        if timestep is None:
            return

        self._status.current_timestep = timestep
        if timestep not in self._status.history:
            self._status.history[ self._status.current_timestep ] = {
                "list": [],
                "map" : {}
            }

        if timestep not in self._timesteps:
            self._timesteps.append(timestep)


    def set_index_tuple(self, index_tuple):
        """
            Sets the current index tuple for the current timestep
        """
        if self._status.current_timestep is None:
            raise Exception("The current timestep has not been set properly!")

        self._status.current_index_tuple = index_tuple
        if self._status.current_index_tuple not in self._status.history[ self._status.current_timestep ]["map"]:
            # This map contains the indexes of the list
            self._status.history[ self._status.current_timestep ]["map"][ index_tuple ] = len( self._status.history[ self._status.current_timestep ]["list"] )

            # This array contains the real value
            self._status.history[ self._status.current_timestep ]["list"].append(self._status.start_value) # None


    def set_start_value(self, value):
        """
            Sets the starting value for the current timestep/scenario_index_tuple
        """
        self._status.start_value = value

    def set_value(self, value):
        """
            Sets the value for the current timestep/scenario_index_tuple
        """
        if self._status.current_timestep is None:
            self.set_start_value(value)
            # raise Exception("The current timestep has not been set properly!")
            return
        if self._status.current_index_tuple is None:
            raise Exception("The current index_tuple has not been set properly!")

        list_index = self._status.history[ self._status.current_timestep ]["map"][ self._status.current_index_tuple ]

        self._status.history[ self._status.current_timestep ]["list"][ list_index ] = value

        # logger.info("=========================================================")
        # logger.info("------------------- set_value ---------------------------")
        # logger.info("self._status.current_timestep: %s", self._status.current_timestep)
        # logger.info("self._status.current_index_tuple: %s", self._status.current_index_tuple)
        # logger.info( "Component Class: %s, Name: %s", self._component_ref.get_class_name(), self._component_ref.name )
        # logger.info( "Nome: %s, Start Value: %r",     self.name,                            self._status.start_value )
        # logger.info( "Nome: %s, Dictionary: %r",      self.name,                            jsonpickle.encode(self._status.history[ self._status.current_timestep ]))
        # logger.info("=========================================================")
        # time.sleep(1)



    def get_current_value(self):
        """
            Gets the value for the current timestep/scenario_index_tuple
        """
        if self._status.current_timestep is None:
            raise Exception("The current timestep has not been set properly!")
        if self._status.current_index_tuple is None:
            raise Exception("The current index_tuple has not been set properly!")


        # logger.info("=========================================================")
        # logger.info("----------- get_current_value -----------------")
        # logger.info( "Component Class: %s, Name: %s", self._component_ref.get_class_name(), self._component_ref.name )
        # logger.info( "Nome: %s, Start Value: %r",     self.name,                            self._status.start_value )
        # logger.info( "Nome: %s, Dictionary: %r",      self.name,                            jsonpickle.encode(self._status.history[ self._status.current_timestep ]))
        # logger.info("self._status.current_timestep: %s", self._status.current_timestep)
        # logger.info("self._status.current_index_tuple: %s", self._status.current_index_tuple)
        # logger.info("=========================================================")
        # time.sleep(1)

        return_value = self._status.start_value

        if self._status.current_index_tuple in self._status.history[ self._status.current_timestep ]["map"]:
            list_index = self._status.history[ self._status.current_timestep ]["map"][ self._status.current_index_tuple ]

            return_value =  self._status.history[ self._status.current_timestep ]["list"][ list_index ]

        return return_value

    def get_previous_value(self):
        """
            Gets the value for the current scenario_index_tuple in the previous timestep
        """
        if self._status.current_timestep is None:
            raise Exception("The current timestep has not been set properly!")
        if self._status.current_index_tuple is None:
            raise Exception("The current index_tuple has not been set properly!")


        list_index = self._status.timesteps.index( self._status.current_timestep )

        if list_index > 0:
            """
                If there is at least a previous item in the history
            """
            previous_timestep = self._status.timesteps[ list_index - 1 ]
            return self._status.history[ previous_timestep ]["map"][ self._status.current_index_tuple ]
        else:
            """
                If there is not a previous item in the history it returns the starting value
            """
            return self._status.start_value
