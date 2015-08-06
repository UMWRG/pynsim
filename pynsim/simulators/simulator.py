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

class Simulator(object):

    network = None
    def __init__(self, network=None):
        self.engines = []
        #User defined timeseps
        self.timesteps = []
        self.network=network

    def __repr__(self):
        my_engines=",".join([m.name for m in self.engines])
        return "Simulator(engines=[%s])"%(my_engines)

    def start(self):

        logging.info("Starting simulation")

        if self.network is None:
            logging.critical("No network to simulate!")
            return

        if len(self.timesteps) == 0:
            logging.critical("No timesteps specified!")
            return

        for idx, timestep in enumerate(self.timesteps):
            self.network.pre_process()
            self.network.set_timestep(timestep, idx)
            logging.debug("Setting up network")
            self.network.setup(timestep)
            
            logging.debug("Setting up institutions")
            self.network.setup_institutions(timestep)
            
            logging.debug("Setting up links")
            self.network.setup_links(timestep)
            
            logging.debug("Setting up nodes")
            self.network.setup_nodes(timestep)
            
            logging.debug("Starting engines")
            for engine in self.engines:
                logging.debug("Running engine %s", engine.name)
                engine.timestep = timestep
                engine.timestep_idx = idx
                engine.run()

            self.network.post_process()

        logging.debug("Finished")

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

    def set_timesteps(self, timesteps, start_time=None, frequency=None, periods=None):
        if timesteps:
            self.timesteps = timesteps
        else:
            raise Exception("Not implemented yet.")
