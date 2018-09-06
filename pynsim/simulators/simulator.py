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

    def __init__(self, network=None, record_time=False, progress=False, max_iterations=1):
        self.engines = []
        #User defined timeseps
        self.timesteps = []
        self.record_time = record_time
        self.network = network
        self.max_iterations = max_iterations
        # Track the cumilative time of the setup functions for the network,
        # nodes links and institutions. Also tracks the cumulative time of each
        # engine run. This dict should show where a slow-down is occurring. For
        # more details, the timings of each node, link & instution can be found
        # in the network.timing property.
        self.timing = {'network': 0, 'nodes': 0, 'links': 0, 'institutions': 0,
                       'engines': {}}

        self.progress = progress
        self.current_timestep = None

    def __repr__(self):
        my_engines = ",".join([m.name for m in self.engines])
        return "Simulator(engines=[%s])" % (my_engines)

    def start(self):
        # Provide dummy function to simplify code below
        def tqdm(iterable, **kwargs):
            return iterable
        if self.progress:
            # If tqdm is installed, use tqdm for printing a progressbar
            try:
                from tqdm import tqdm
            except ImportError:
                logging.warn("Please install 'tqdm' to display progress bar.")

        for engine in self.engines:
            self.timing['engines'][engine.name] = 0

        logging.info("Starting simulation")

        if self.network is None:
            logging.critical("No network to simulate!")
            return

        if len(self.timesteps) == 0:
            logging.critical("No timesteps specified!")
            return

        for engine in self.engines:
            logging.debug("Setting up engine %s", engine.name)
            engine.initialise()

        for idx, timestep in tqdm(enumerate(self.timesteps),
                                  total=len(self.timesteps)):

            self.current_timestep = timestep

            self.network.set_timestep(timestep, idx)

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

        for engine in self.engines:
            logging.debug("Teearing Down engine %s", engine.name)
            engine.teardown()
        
        logging.debug("Finished")

    def plot_timing(self):
        """
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

        if type(depends_on) != list:
            depends_on = [depends_on]

        for dependant in depends_on:
            if dependant not in self.engines:
                raise Exception("Engine %s depends on %s but it is not in the"
                                " list of engines.")

        self.engines.append(engine)

    def add_network(self, network):
        self.network = network

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
