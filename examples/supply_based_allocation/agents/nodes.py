# -*- coding: utf-8 -*-
"""This file defines node types used in the routing model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) Eawag: Swiss Federal Institue of Aquatich Science and Technology
"""

from pynsim import Node
from copy import copy


class Reservoir(Node):
    """A surface reservoir with a monthly target release.

    Variables: S (storage)
               actual_release
    Parameters: min_stor
                max_stor
                init_stor
                target_release
                inflow
    """

    _properties = {'S': None,
                   'actual_release': None,
                   'min_stor': None,
                   'max_Stor': None,
                   'init_stor': None,
                   'target_release': None,
                   'inflow': None,
                   }

    def setup(self, t):
        self.target_release = self._target_release[t]
        self.inflow = self._inflow[t]

class Junction(Node):
    _inflow = {}
    _allocation = {}
    _allocation_priority = None
    _allocation_type = None
    _properties = {'inflow':None}

    def setup(self, timestamp):

        self.inflow = self._inflow.get(timestamp, 0)
        self.allocation = self._allocation.get(timestamp)
      
        if len(self.in_links) > 0:
            for in_link in self.in_links:
                self.inflow = self.inflow + in_link.flow

    def consume(self):
        self.inflow = self.inflow + sum([l.flow for l in self.in_links])

    def allocate(self):
        """
            Using the internal allocation rules, allocate flow to the
            connecting links at this time step.
            The default behaviour if there are no rules specified is to 
            split the allocation equally. Any links not specified as priority
            links get the leftover water equally.
        """
        self.non_priority_links = copy(self.out_links)
        allocation_avail   = copy(self.inflow)
        
        if self.allocation is not None:
            #Allocation priority can either be a tuple of links or a link.
            if type(self._allocation_priority) == tuple:
                for i, link in enumerate(self._allocation_priority):
                    allocation = self.allocation[i]
                    alloc_vol = self.set_outflow(link, allocation)
            else:
                link = self._allocation_priority
                allocation = self.allocation
                alloc_vol = self.set_outflow(link, allocation)
            allocation_avail = allocation_avail - alloc_vol

        if allocation_avail < 0:
            raise Exception("Node %s cannot satisfy allocation."%(self.name))
        
        if len(self.non_priority_links) > 0:
            #Split the remaining water equally between remaining links
            link_alloc = (100 / len(self.non_priority_links)) / 100
            for seq in self.non_priority_links:
                seq.flow = allocation_avail * link_alloc

    def set_outflow(self, link, allocation):
        if link not in self.non_priority_links:
            raise Exception("Link %s in the allocation priority not "
                            "connected to node %s"%(link.name, self.name))

        if self._allocation_type == 'pct':
            alloc_volume = self.inflow * (allocation / 100.0)
        else:
            alloc_volume = allocation

        if link.end_node.component_type == 'Farm':
            farm = link.end_node
            alloc_volume = min(farm.demand, alloc_volume)

        link.flow = alloc_volume

        self.non_priority_links.remove(link)

        return alloc_volume

class Consumption(Node):
    def consume(self):
        self.inflow = sum([l.flow for l in self.in_links])
        self.deficit = self.demand - self.inflow

class Farm(Consumption):
    _demand = {}
    _properties = {'inflow': None,
                    'deficit' : None,
                   'demand': 0,}
    def setup(self, timestamp):
        self.demand = self._demand.get(timestamp, self._properties['demand'])

class Urban(Consumption):
    _demand = {}
    _properties = {'inflow': None,
                    'deficit' : None,
                   'demand' : None}
    def setup(self, timestamp):
        self.demand = self._demand.get(timestamp, 0)
