#    (c) Copyright 2014, University of Manchester
#
#    This file is part of PyNSim.
#
#    PyNSim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNSim i`s distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNSim.  If not, see <http://www.gnu.org/licenses/>.

from pynsim import Engine 

class DeficitAllocation(Engine):

    name   = """A pyomo-based engine which allocates water throughout a whole
    network in a single time-step."""
    target = None

    def update(self):
        """
            Need to do some stuff here
        """
        
        #find all the irrigation nodes and calculate their deficits.
        irrigation_nodes = [] 
        deficits = {}
        for n in self.target.nodes:
            if n.type == 'irrigation':
                irrigation_nodes.append(n)
                deficits[n.name] = n.deficit

        for irr in irrigation_nodes:
            if irr.demand > irr.max_allowed:
                node_deficit = irr.demand - irr.max_allowed
                irr.deficit = irr.deficit + node_deficit
