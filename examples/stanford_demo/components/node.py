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

from pynsim import Node

class Junction(Node):
    type = 'junction'
    _properties = dict(
        max_capacity=1000,
    )

class IrrigationNode(Node):
    """
        A general irrigation node, with proprties demand, max and deficit.
        At each timestep, this node will use its internal seasonal
        water requirements to set a demand figure. THe allocator will then
        calculate deficit based on its max allowed and demand.
    """
    type = 'irrigation'
    _properties = dict(
        #percentage
        max_allowed = 100,
        demand = 0,
        deficit=0,
    )

    def setup(self, timestamp):
        """
            Get water requirements for this timestep based on my internal
            requirements dictionary.
        """
        self.demand = self._seasonal_water_req[timestamp]

class CitrusFarm(IrrigationNode):
    _seasonal_water_req = {
        "2014-01-01": 100,
        "2014-02-01": 200,
        "2014-03-01": 300,
        "2014-04-01": 400,
        "2014-05-01": 500,
    }

class VegetableFarm(IrrigationNode):
    _seasonal_water_req = {
        "2014-01-01": 150,
        "2014-02-01": 250,
        "2014-03-01": 350,
        "2014-04-01": 450,
        "2014-05-01": 550,
    }

class SurfaceReservoir(Node):
    """
        Node from which all the other nodes get their water. This reservoir
        is given its water allocation from its institution -- the ministry of water.
    """
    type = 'surface reservoir'
    _properties = dict(
        release = 0,
        capacity = 1000,
        max_release = 1000,
    )

    def setup(self, timestamp):
        """
            The ministry of water has given me my release details, so there
            is no need for me to set anything up myself.
        """
        pass

