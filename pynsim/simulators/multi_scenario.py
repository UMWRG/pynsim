#    (c) Copyright 2014-2020, University of Manchester
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

class MultiScenarioSimulator(object):
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

    def start(self, initialise=True):
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
