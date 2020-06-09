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

class Engine(object):
    name   = "A generic pynsim engine"
    target = None
    simulator = None
    UUID = None

    def __init__(self, target):
        self.target = target
        self.timestep = None
        #indicates numerically the current timestep
        self.timestep_idx = None
        self.iteration = None
        self.UUID = None

    def run(self):
        pass

    def initialise(self):
        pass

    def teardown(self):
        pass
