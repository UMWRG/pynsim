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
import os
import time
import pickle
from copy import deepcopy, copy
import sys
import datetime
from pynsim.history import Map
import json
import jsonpickle

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

from .component_status import ComponentStatus


class Component(object):
    """
        A top level object, from which Networks, Nodes, Links and Institions
        derive. This object is what a model performs its calculations on.
    """
    name = None
    description = None
    base_type = 'component'

    # This dict contains both the current scenarios properties names
    # and the status properties names
    _properties = dict()
    #_history = dict()
    # To avoid exporting the history of every property, property names can
    # be specified here to explictly define which properties are results
    # (and are therefore to be exported).
    _result_properties = []

    # List of fields that will be managed through the scenario manager.
    # They are set at class level.
    # These are the parameter set for providing the full scenarios
    _scenario_parameters = dict()

    # List of fields that does not vary through the simulation
    # _invariant_parameters = dict()

    # This dictionary contains the fields that represents the internal status.
    # These fields will be managed by the component status object
    # _internal_status_fields = dict()

    def __init__(self, name, simulator=None, **kwargs):
        """
            This method initialize the component
        """
        # Reference to the simulator
        self._simulator = None

        self.bind_simulator(simulator) # To properly bind the simulator!

        self.component_type = self.__class__.__name__
        if name is None:
            raise Exception("The 'name' of a pynsim component is mandatory and unique inside the same components set!")

        self.name = name
        # self._history = dict()

        self._status = ComponentStatus(component_ref = self)

        """
            IF:
                True => the component raises an exception if scenario_id is found None in any operation
                False => the component temporary allows scenario_id being None in any operation
        """
        self.current_scenario_id_mandatory_flag = False

        for k, v in self._properties.items():
            setattr(self, k, deepcopy(v))

        for k, v in kwargs.items():
            """
                Eventual properties set at definition time
            """

            if k == "_scenario_parameters":
                setattr(self, k, v)
            elif k in self._properties:
                setattr(self, k, v)
            elif k in self._scenario_parameters:
                setattr(self, k, v)
            else:
                raise Exception("Invalid property %s. Allowed properties are: %s" % (k, self._properties.keys()))


    def __setattr__(self, name, value):
        """
            This method intercepts the calls to set every attribute of the class objects.
            - If the attribute owns to "_properties" object, it sends the value to the "overall" object
            - If the attribute owns to "_scenario_parameters" object, it sends the value to the "scenario_manager" object
            In any case the value is also set as object attribute
        """
        if name is not "_simulator" and self._simulator is None:
            raise Exception("The current Component does not have any simulator assigned!")

        if name == "_scenario_parameters":
            pass
        else:
            if name in self._properties:
                """
                    If the property is valid for status
                """
                self._simulator.get_overall_status().set_value(self.name, name, self._status.get_current_scenario_id(), self._status.get_current_timestep(), value)

            elif name in self._scenario_parameters:
                self._simulator.get_scenario_manager().add_scenario(
                    object_type=self.__class__.__name__,
                    object_name = self.name,
                    object_reference = self,
                    property_name=name,
                    property_data=value
                )
            else:
                pass

        super().__setattr__(name, value) # This allows to propagate the __setattr__ to the object itself



    def __getattribute__(self, name):
        """
            This method intercepts the calls to get every attribute value of the class objects.
            - If the attribute is the "_history" array, the array is returned by the "overall_status" object
            - If the attribute owns to "attrs_to_return_directly" array,  the value is returned as it is
            - If the attribute owns to "_properties" object, it returns the current value of the component for the current timestep and scenario
            - Otherwise the returned value is the one of the object attribute
        """
        attrs_to_return_directly=[
            "__class__", "_properties","_scenario_parameters",
            "name", "description","base_type","_simulator",
            "_status", "component_type", "_history",
            "_scenario_parameters"
        ]
        if name == "_history":
            """
                The history has to come from the overall history manager
            """
            local_name =  self.name
            local_status = self._status
            local_simulator = self._simulator

            return local_simulator.get_overall_status().get_component_history_as_dict(local_name, local_status.get_current_scenario_id())
        elif name in attrs_to_return_directly:
            """
                This items has to be returned as they are
            """
            return object.__getattribute__(self, name)
        else:
            local_properties = self._properties
            if name in local_properties:
                """
                    The values have to come from the history managaer
                """
                local_name =  self.name
                local_status = self._status
                local_simulator = self._simulator
                # return local_simulator.get_overall_status().get_value(local_name, name, local_status.get_current_scenario_id(), local_status.get_current_timestep())
                return self.get_current_history_value(name)
            elif name in self._scenario_parameters:
                """
                    In this point we are returning a value composing the scenario
                """
                #print("Name: {}, Value: {}".format(name, object.__getattribute__(self, name)))
                pass
            else:
                """
                    All the rest
                """
                pass
        return object.__getattribute__(self, name)


    def set_current_scenario_id_mandatory_flag(self):
        """
            To set a flag to eventually make mandatory the scenario_id settings
            IF:
                True => the component raises an exception if scenario_id is found None in any operation
                False => the component temporary allows scenario_id being None in any operation
        """
        self.current_scenario_id_mandatory_flag = True
        self._status.set_current_scenario_id_mandatory_flag()

    def get_multi_scenario_history(self, prop_name):
        """
            Returns the history getting it from the multi scenario results object
        """
        return self._simulator.get_overall_status().get_property_history_as_array(self.name, prop_name, self._status.get_current_scenario_id())

    def get_multi_scenario_history_all_properties(self, properties_allowed=None):
        """
            Returns the history getting it from the multi scenario results object
        """
        return self._simulator.get_overall_status().get_component_history_as_dict(self.name, self._status.get_current_scenario_id(), properties_allowed=properties_allowed)

    def replace_internal_value(self, name, value):
        """
            This is called explicitly to replace the values without passing from __setattr__
        """
        super().__setattr__(name, value) # This allows to propagate the __setattr__ to the object itself

    def get_status(self):
        """
            Returns the _status object
        """
        return self._status

    def set_current_scenario_id(self, current_scenario_id):
        """
            Sets the current scenario_id
        """
        self._status.set_current_scenario_id(current_scenario_id)

    def reset_current_scenario_id(self):
        """
            Resets the current scenario_id
        """
        self._status.reset_current_scenario_id()


    def set_current_timestep(self, timestep):
        """
            Sets the current timestep for the component to be used as reference by set and get property values
        """
        self._status.set_current_timestep(timestep)

    @classmethod
    def get_class_name(cls):
        """
            Return the class name.
        """
        return cls.__name__

    def get_object_name(self):
        """
            Return the object name.
        """
        return self.name

    def bind_simulator(self, simulator=None):
        """
            Command to set the simulator reference
        """
        if self._simulator is None:
            if simulator is not None:
                self._simulator = simulator
                simulator.register_component(self) # Registering the component into the simulator
            else:
                raise Exception("The simulator reference cannot be None")

    def get_simulator(self):
        """
            Returns the simulator reference
        """
        return self._simulator

    def get_current_history_value(self, property_name, default_value=None):
        """
            Returns the property value identified by current timestep and current scenario id
        """
        comp_history = self._history

        if property_name in comp_history:
            """
                This is a computed property
            """
            prop_history = comp_history[property_name]
            if len(prop_history) == 0:
                if default_value is None:
                    raise Exception(f"The property '{property_name}' has not any items!")
                else:
                    return default_value
            else:
                return prop_history[ len(prop_history) - 1 ]

        if property_name in self._scenario_parameters:
            """
                This is a scenario parameter
            """
            prop_history = object.__getattribute__(self, property_name)
            # print(prop_history)
            # print(self._status.get_current_scenario_id())
            # print(self._status.get_current_timestep())
            if isinstance(prop_history, dict):
                return prop_history[str(self._status.get_current_timestep())]
            else:
                return prop_history



        else:
            """
                Not defined
            """
            if default_value is None:
                print(comp_history)
                raise Exception(f"The property '{property_name}' is not defined!")
            else:
                return default_value


    def get_previous_history_value(self, property_name, default_value=None):
        """
            if the value is found in history, is returned as previous value.
            default otherwise
        """
        comp_history = self._history

        if property_name in comp_history:
            prop_history = comp_history[property_name]
            if len(prop_history) == 0:
                if default_value is None:
                    raise Exception(f"The property '{property_name}' has not any items!")
                else:
                    return default_value
            else:
                return prop_history[-1]
        else:
            if default_value is None:
                raise Exception(f"The property '{property_name}' is not defined!")
            else:
                return default_value

    def get_history(self, attr_name=None, properties_allowed=None):
        """
            Return a dictionary, keyed on timestep, with each value of the
            attribute at that timestep.
        """
        if attr_name is not None:
            return self._history.get(attr_name, None)
        else:
            return self._simulator.get_overall_status().get_component_history_as_dict(self.name, self._status.get_current_scenario_id(), properties_allowed=properties_allowed)



    def reset_history(self):
        """
            Reset the _history dict. This is useful if a simulator instance is
            used for multiple simulations.
        """
        for k in self._properties:
            self._history[k] = []

    def get_properties(self):
        """
            Get all the properties for this component
            (as defined in _properties)
        """
        properties = dict()
        for k in self._properties:
            properties[k] = getattr(self, k)
        return properties

    def post_process(self):
        for k in self._properties:
            attr = getattr(self, k)
            if isinstance(attr, dict) or isinstance(attr, list):
                self._history[k].append(deepcopy(attr))
            else:
                self._history[k].append(attr)

    def __repr__(self):
        return "Component(name=%s)" % (self.name)

    # def setup(self, timestamp):
    #     """
    #         Setup function to be overwritten in each component implementation
    #     """
    #     pass

    def setup(self, t):
        """
            Setup function to be overwritten in each component implementation
            This is mandatory in the subclass id overloading the property:
            super().setup(t)
        """
        for prop_name in self._scenario_parameters:
            setattr(self, self._scenario_parameters[prop_name], self.get_current_history_value(prop_name))


    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def validate_history(self):
        """
            Check whether this comonent's history can be exported
        """
        try:
            json.dumps(self._history)
        except TypeError:
            logging.warn("History of %s %s is not JSON compatible. Trying to pickle...", self.base_type, self.name)
            pickle.dumps(self._history)
        except TypeError:
            logging.critical("History of %s %s cannot be exported. Skipping.", self.base_type, self.name)
            return False

        return True



    def get_status_repr(self):
        """
            Returns a representation of the full component
        """
        return repr(self._status)
