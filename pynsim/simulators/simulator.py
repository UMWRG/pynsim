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
from pynsim.multi_scenario import ScenariosManager, OverallStatus

import jsonpickle
import json
from datetime import datetime
import os

import pprint

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

class EngineIterator:
    """ Iterator and context manager for running engines.

    This object can be used as a context manager for iterating engines within
    a `Simulator`. Within the context the manager can be used as an iterator
    to cycle through the engines, in order, for a number of iterations. Iteration
    is termined if `max_iterations` are reached or one of the engines raises
    a `StopIteration` exception within the context.
    """
    def __init__(self, simulator, max_iterations=1):
        self.simulator = simulator
        self.max_iterations = max_iterations
        self._current_engine_index = None
        self._current_iteration = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is StopIteration:
            # Stop iteration is a valid exception to stop the context/iteration
            return True
        return False

    def __iter__(self):
        self._current_engine_index = 0
        self._current_iteration = 1
        return self

    def __next__(self):
        current_engine = self.simulator.engines[self._current_engine_index]
        current_iteration = self._current_iteration
        if current_iteration > self.max_iterations:
            raise StopIteration
        self._current_engine_index = (self._current_engine_index + 1) % len(self.simulator.engines)
        if self._current_engine_index == 0:
            self._current_iteration += 1
        return current_iteration, current_engine

    def next(self):
        """
        This is for python 2 compatibility
        """
        return self.__next__()


class Simulator(object):

    network = None

    def __init__(self, network=None, record_time=False, progress=False, max_iterations=1, save_components_history=True):
        """
            Simulator INIT method
        """
        self.engines = []
        #User defined timesteps
        self.timesteps = []
        self.record_time = record_time
        if network is not None:
            self.network = network

        self.max_iterations = max_iterations
        # Track the cumulative time of the setup functions for the network, nodes links and institutions.
        # Also tracks the cumulative time of each engine run.
        # This dict should show where a slow-down is occurring.
        # For more details, the timings of each node, link & instution can be found
        # in the network.timing property.
        self.timing = {'network': 0, 'nodes': 0, 'links': 0, 'institutions': 0,
                       'engines': {}}

        self.progress = progress

        # This is the current timestep of the simulation
        self.current_timestep = None

        # This is the current scenario id, set by the iterations
        self.current_scenario_id = None

        # This is the current scenario id, set by the iterations. goes from 1 to the last scenario count
        self.current_scenario_serial_index = 0

        # This flag allows to decide if saving the component history or just having the last timestep iteraion data at the end of the simulation
        self._save_components_history = save_components_history
        # This is to manage all the scenarios
        self.scenarios_manager = ScenariosManager(save_components_history=save_components_history)
        # This object manages the status of the full network
        self.overall_status = OverallStatus(save_components_history=save_components_history)
        # List of the registered components
        self.components_registered_list = []
        # Priority for the loops
        self.loop_priority = "timestep"

    def __repr__(self):
        my_engines = ",".join([m.name for m in self.engines])
        return "Simulator(engines=[%s])" % (my_engines)

    def get_save_components_history_flag(self):
        """
            Returns the flag value
        """
        return self._save_components_history

    def get_scenario_manager(self):
        """
            Returns the "scenario manager" object
        """
        return self.scenarios_manager

    def get_full_scenarios_count(self):
        """
            Returns the "scenario manager" get_full_scenarios_count property
        """
        return self.scenarios_manager.get_full_scenarios_count()

    def get_current_scenario_index(self):
        """
            Returns the "current scenario index" property from multiscenario object
            !! deprecated !!!
        """
        return self.scenarios_manager.get_current_index()


    def get_overall_status(self):
        """
            Returns the "overall status" object
        """
        return self.overall_status

    def get_defined_scenarios_count(self):
        """
            Returns the number of defined scenarios
        """
        return self.overall_status.get_scenarios_count()

    def get_results_scenarios_indexes_list(self):
        """
            Returns all the defined scenarios indexes defined by overall
        """
        return self.overall_status.get_scenarios_indexes_list()

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
        return self.overall_status.export_status_indexed_by_scenarios()

    def export_status_indexed_by_scenarios_to_file(self, filepath):
        """
            Save the exported data to a file
        """
        file = open(filepath,"w")

        data = self.export_status_indexed_by_scenarios()
        file.write(pprint.pformat(data))

        file.close()

    def initialise(self):
        """
            Init method
        """
        logging.info("Initialising simulation")

        if self.network is None:
            raise RuntimeError("No network to simulate!")

        if len(self.timesteps) == 0:
            raise RuntimeError("No timesteps specified!")

        for engine in self.engines:
            logging.debug("Setting up engine %s", engine.name)
            engine.initialise()

    def register_component(self, component_ref):
        """
            Method needed to register the component into the simulator
        """
        self.components_registered_list.append(component_ref)

    def show_registered_components(self):
        """
            This method is implemented to show all the registered components to the simulator
        """
        for comp in self.components_registered_list:
            logging.info("Component Class Name %s", comp.get_class_name())
            logging.info("Object Name %s", comp.get_object_name())

    def get_scenarios_iterator(self, format="full"):
        """
            Shortcut to return the scenario manager iterator
        """
        return self.get_scenario_manager().get_scenarios_iterator(format)

    def iterate_scenarios_for_timestep(self, tqdm):
        """
            This method allows the iterations primarily by timesteps and internally by scenarios
        """
        """
            Iteration over the timesteps
        """
        for idx, timestep in tqdm(enumerate(self.timesteps),
                                  total=len(self.timesteps)):

            # logging.error("==================================================================================")
            # logging.error("Timestep %s", timestep)
            # logging.error("==================================================================================")

            # Setting the current timestep, used as reference
            self.current_timestep = timestep
            for component_registered in self.components_registered_list:
                """
                    Setting the current timestep for each registered component.
                    This is needed to properly manage the history
                """
                component_registered.set_current_timestep(timestep)


            self.network.set_timestep(timestep, idx)
            """
                Iteration over all the scenarios
            """
            scenarios_manager = self.get_scenario_manager()
            self.current_scenario_serial_index = 0
            for scenario_item in scenarios_manager.get_scenarios_iterator("full"):
                """
                    Gets current scenario data and index
                """
                scenario_item_data  = scenario_item["data"]
                scenario_id = scenario_item["scenario_id"]

                self.current_scenario_id = scenario_id

                # logging.warning("+================================================================")
                # logging.warning("| scenario_id %s", scenario_id)
                # logging.warning("+================================================================")

                self.run_single_simulation_step(
                    idx,
                    timestep,
                    scenario_id,
                    scenario_item_data
                )

                # Incrementing scenario counter
                self.current_scenario_serial_index = self.current_scenario_serial_index + 1


    """=========================================="""

    def iterate_timesteps_for_scenario(self, tqdm):
        """
            This method allows the iterations primarily by scenarios and internally by timesteps
        """
        """
            Iteration over all the scenarios
        """
        scenarios_manager = self.get_scenario_manager()
        self.current_scenario_serial_index = 0
        for scenario_item in scenarios_manager.get_scenarios_iterator("full"):
            """
                Gets current scenario data and index
            """
            scenario_item_data  = scenario_item["data"]
            scenario_id = scenario_item["scenario_id"]

            self.current_scenario_id = scenario_id

            # logging.warning("+================================================================")
            # logging.warning("| scenario_id %s", scenario_id)
            # logging.warning("+================================================================")
            """
                Iteration over the timesteps
            """
            for idx, timestep in tqdm(enumerate(self.timesteps),
                                      total=len(self.timesteps)):

                # logging.error("==================================================================================")
                # logging.error("Timestep %s", timestep)
                # logging.error("==================================================================================")

                # Setting the current timestep, used as reference
                self.current_timestep = timestep
                for component_registered in self.components_registered_list:
                    """
                        Setting the current timestep for each registered component.
                        This is needed to properly manage the history
                    """
                    component_registered.set_current_timestep(timestep)


                self.network.set_timestep(timestep, idx)

                self.run_single_simulation_step(idx, timestep, scenario_id, scenario_item_data)

            # Incrementing scenario counter
            self.current_scenario_serial_index = self.current_scenario_serial_index + 1


    def get_current_scenario_serial_index(self):
        """
            Returns the current scenario serial index
        """
        return self.current_scenario_serial_index

    def run_single_simulation_step(self, idx=None, timestep=None, scenario_id=None, scenario_item_data=None):
        """
            Setup all network components and runs all engines over a defined couple (timestep, scenario_id)
        """
        logging.debug("idx: %r", idx)
        logging.debug("timestep: %r", timestep)
        logging.debug("scenario_id: %r", scenario_id)
        logging.debug("scenario_item_data: %r", scenario_item_data)

        for component_item in scenario_item_data:
            """
                Setting the scenario_id, of the current scenario, for every component
            """
            component_item["object_reference"].set_current_scenario_id(scenario_id)
            # replacing the values from the multiscenario obj
            component_item["object_reference"].replace_internal_value(component_item["property_name"],component_item["property_data"])

        logging.debug("Setting up network")
        t = time.time()
        self.network.setup(timestep)
        self.timing['network'] += time.time() - t

        logging.debug("Setting up components")
        setup_timing = self.network.setup_components(timestep, self.record_time)

        if self.record_time:
            self.timing['institutions'] += setup_timing['institutions']
            self.timing['links']        += setup_timing['links']
            self.timing['nodes']        += setup_timing['nodes']

        logging.debug("Starting engines")

        # Cycle through the engines up to the maximum number of iterations
        # The context manager catches any `StopIteration` exceptions from the engines
        # and terminates the context.
        with EngineIterator(self, max_iterations=self.max_iterations) as manager:
            for iteration, engine in manager:
                logging.debug("Running engine %s", engine.name)

                if self.record_time:
                    t = time.time()

                engine.iteration = iteration
                engine.timestep = timestep
                engine.timestep_idx = idx
                engine.run()

                if self.record_time:
                    self.timing['engines'][engine.name] += time.time() - t

        self.network.post_process()

    def set_loop_priority(self, priority="timestep"):
        """
            Allows to setup which loop priority to use .
        """
        if priority not in ["timestep", "scenario"]:
            raise Exception("You must select a valid value as loop priority: 'timestep', 'scenario'")
        self.loop_priority = priority


    def start(self, initialise=True):
        """
            This method starts and run all the simulation until the end
        """
        # Provide dummy function to simplify code below
        def tqdm(iterable, **kwargs):
            return iterable
        if self.progress:
            # If tqdm is installed, use tqdm for printing a progressbar
            try:
                from tqdm import tqdm
            except ImportError:
                logging.warn("Please install 'tqdm' to display progress bar.")

        # Testing that every engine has the simulator setup properly
        for engine in self.engines:
            if engine.simulator is None:
                raise Exception("The engine X has not the simulator reference properly setup!")


        for engine in self.engines:
            self.timing['engines'][engine.name] = 0

        logging.info("Starting simulation")

        if initialise is True:
            self.initialise()

        """
            Iterating the engines with the chosen priority
        """
        if self.loop_priority == "scenario":
            self.iterate_timesteps_for_scenario(tqdm)
        elif self.loop_priority == "timestep":
            self.iterate_scenarios_for_timestep(tqdm)
        else:
            raise Exception("You must select a valid value for the loop_priority: 'timestep', 'scenario'")

        for engine in self.engines:
            logging.debug("Tearing Down engine %s", engine.name)
            engine.teardown()

        logging.debug("Finished")

        # logging.warning("Overall %r", self.overall_status.dump())

        if self.overall_status.get_scenarios_count() > 1:
            # If the scenarios count is more than 1 the user needs to set the scenario id before getting any data
            # Otherwise, 1 single scenario can be queried using the last (and the only) scenario id,
            # i.e. not specificing the scenario explicitly
            scenarios_manager = self.get_scenario_manager()
            for scenario_item in scenarios_manager.get_scenarios_iterator("full"):
                scenario_item_data  = scenario_item["data"]
                for component_item in scenario_item_data:
                    """
                        Setting the scenario_id, of the current scenario, for every component
                    """
                    component_item["object_reference"].reset_current_scenario_id()
                    # This force the user to set the scenario id to query the data afterwards!
                    component_item["object_reference"].set_current_scenario_id_mandatory_flag()

    def plot_timing(self):
        """
            Plots the timing
        """
        #Import seaborn to prettify the graphs if possible
        try:
            import seaborn
        except:
            pass

        try:
            import matplotlib.pyplot as plt

            width = 0.35

            s = [self.timing['nodes'], self.timing['links'],
                 self.timing['institutions'],
                 sum(self.timing['engines'].values())]

            fig, ax = plt.subplots()

            rects1 = ax.bar([0, 1, 2, 3], s, width, color='r')
            ax.set_xticks([0.15, 1.15, 2.15, 3.15])
            ax.set_xticklabels(('Nodes', 'Links', 'Institutions', 'Engines'))
            ax.set_ylabel('Time')
            plt.title('Timing')

            plt.show(block=True)

        except ImportError:
            logging.critical("Cannot plot. Please ensure matplotlib "
                             "and networkx are installed.")

    def plot_engine_timing(self):
        """
            Plots the engine timing
        """
        #Import seaborn to prettify the graphs if possible
        try:
            import seaborn
        except:
            pass
        try:
            import matplotlib.pyplot as plt

            width = 0.35

            s = self.timing['engines'].values()
            names = self.timing['engines'].keys()
            plt_axes = []
            plt_axes_offset = []
            for i, n in enumerate(names):
                plt_axes.append(i)
                plt_axes_offset.append(i + 0.15)

            fig, ax = plt.subplots()

            rects1 = ax.bar(plt_axes, s, width, color='r')
            ax.set_xticks(plt_axes_offset)
            ax.set_xticklabels(list(names))
            ax.set_ylabel('Time')
            ax.set_xlabel('Engine')
            plt.title('Timing')

            try:
                import mpld3
                i = 0
                for r in rects1:
                    tooltip = mpld3.plugins.LineLabelTooltip(r, label=names[i])
                    mpld3.plugins.connect(fig, tooltip)
                    i = i + 1
                mpld3.show()
            except Exception as e:
                logging.exception(e)
                logging.warn("For tooltips, install mpld3 (pip install mpld3)")
                plt.show(block=True)

        except ImportError:
            logging.critical("Cannot plot. Please ensure matplotlib "
                             "and networkx are installed.")

    def pause(self):
        pass

    def stop(self):
        pass

    def add_engine(self, engine, depends_on=[]):
        """
            Adds an engine to the simulator
        """

        if type(depends_on) != list:
            depends_on = [depends_on]

        for dependant in depends_on:
            if dependant not in self.engines:
                raise Exception("Engine %s depends on %s but it is not in the"
                                " list of engines.")

        self.engines.append(engine)

        engine.simulator = self


    def __setattr__(self, name, value):
        """
            Used to operate on simulator attributes before the eventual settings
        """
        super().__setattr__(name, value) # This allows to propagate the __setattr__ to the object itself

        if name == "network":
            """
                Linking the network to the simulator
            """
            value.bind_simulator(self)

    def set_timesteps(self, timesteps, start_time=None, frequency=None,
                      periods=None, end_time=None):
        """Set time steps on the simulator. Time steps need to be iterable. If
        sufficent information is passed to this function, a time index is
        generated as pandas.DateTimeIndex.
        """

        if timesteps is not None:
            # Check if iterable
            try:
                _ = [t for t in timesteps]
                self.timesteps = timesteps
            except TypeError:
                logging.critical("Cannot set timesteps. Timesteps must be "
                                 "iterable.")
        else:
            try:
                import pandas as pd
                # Generate time index
                self.timesteps = pd.date_range(start=start_time, end=end_time,
                                               periods=periods, freq=frequency)
            except ImportError:
                logging.critical("Cannot set timestep. Please ensure pandas is"
                                 " installed.")

    def reset_history(self):
        """Reset the history of all components used in this simulation.
        """
        self.network.reset_history()
        for node in self.network.nodes:
            node.reset_history()
        for link in self.network.links:
            link.reset_history()
        for institution in self.network.institutions:
            institution.reset_history()


    def export_history(self, property_name, export_file):
        """
        Export the history of a given set of properties to a CSV file.

        Args:

            property_name (string or list of strings): Properties that will be
                exported.

            export_file (string): Full path to the file path. Existing files
                will be overwritten.

        Returns:

            None

        Raises:

        """
        try:
            import pandas as pd

            export_data = pd.DataFrame(index=self.timesteps)

            if isinstance(property_name, str):
                property_name = [property_name]

            for prop in property_name:
                if prop in self.network.get_properties():
                    export_data['%s %s' % (self.network.name, prop)] = \
                        self.network._history[prop]

            for n in self.network.nodes:
                for prop in property_name:
                    if prop in n.get_properties():
                        export_data['%s %s' % (n.name, prop)] = n._history[prop]

            for l in self.network.links:
                for prop in property_name:
                    if prop in l.get_properties():
                        if len(export_data.columns) > 0:
                            logging.info("INFO: Some nodes have the same"
                                         "property %s as this link %s"
                                         % (property_name, l.name))
                        export_data['%s %s' % (l.name, prop)] = l._history[prop]

            for i in self.network.institutions:
                for prop in property_name:
                    if prop in i.get_properties():
                        if len(export_data.columns) > 0:
                            logging.info("INFO: Some nodes or links have the"
                                         "same property %s as this institution"
                                         "(%s)" % (property_name, i.name))
                        export_data['%s %s' % (i.name, prop)] = i._history[prop]

            if len(export_data.columns) == 0:
                logging.warn("No components found with property %s"
                             % property_name)
                return
            else:
                export_data.to_csv(export_file)
        except ValueError:
            logging.critical("Unable to export export %s to csv. Only simple types (numbers, strings) can be"
                               "exported to CSV.", property_name)

        except ImportError:
            logging.critical("Cannot export history. Please ensure pandas is"
                             "installed." % property_name)
