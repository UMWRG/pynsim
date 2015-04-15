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

from pynsim import Institution

class WaterDepartment(Institution):
    name = "Government department in charge of water"

    _properties = dict(
        flow_requirements=[],
        allocation       = 1000
    )

    #Based on rainfall in mm, how much will the surface reservoir get?
    _release_curve = (
        (0 , 100),
        (10, 150),
        (20, 250),
        (30, 500),
        (40, 750),
        (50, 1000),
        (60, 1250),
        (70, 1500),
        (80, 1750),
        (90, 2000),
        (100, 2500),
    )

    def setup(self, timestamp):
        """
            Based on the current amount of water coming in, allocate
            some water to the surface reservoir.
        """
        incoming_water = self.network.incoming_water_qty[timestamp]
       
        #find the surface reservoir
        reservoir = self.getnodes("surface reservoir")[0]

        #find the amount to give to the reservoir and then give it (set the
        #release attribute)
        for alloc in self._release_curve:
            if alloc[0] <= incoming_water:
                continue
            else:
                reservoir.release = alloc[1]
                break
    
    def getnodes(self, agent_type):
        """
            Convenience function to get the nodes in a network of a certain type
        """
        nodes = []
        for n in self.nodes:
            if n.type == agent_type:
                nodes.append(n)
        return nodes

class IrrigationDecisionMaker(Institution):
    name = "Authority in charge of allocating water to farms"

    _properties = dict(
        allocation=[],
    )
    
    #This institution does allocation based on a simple weighting calculation.
    #The weights are defined here in this internal dictionary.
    _allocation_weight = {
        'vegetable' : 0.7,
        'citrus'    : 0.8,
    }

    def setup(self, timestamp):

        #find the surface reservoir
        reservoir = None
        for n in self.network.nodes:
            if n.type == 'surface reservoir':
                reservoir = n
                break
        
        release = reservoir.release

        #get the weight of citrus and veg farms and initialise the total weight
        #sum.
        weight_sum = 0
        citrus_weight = self._allocation_weight['citrus']
        veg_weight    = self._allocation_weight['vegetable']
        
        #Add up the weights.
        for n in self.nodes:
            if n.agent_type == "CitrusFarm":
                weight_sum = weight_sum + citrus_weight
            elif n.agent_type == "VegetableFarm":
                weight_sum = weight_sum + veg_weight
        
        #Get the proportions of the release per farm based on a simple weighting
        #calculation.
        citrus_release = citrus_weight/weight_sum * release
        veg_release    = veg_weight/weight_sum    * release
        
        #The proportion of release per farm is the maximum each farm can have
        #on this time step. The difference between this value and the farmer's
        #demand is the deficit
        for n in self.nodes:
            if n.agent_type == "CitrusFarm":
                n.max_allowed = citrus_release
            elif n.agent_type == "VegetableFarm":
                n.max_allowed = veg_release 
