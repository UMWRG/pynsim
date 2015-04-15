# -*- coding: utf-8 -*-
"""This file defines a river network used for the routing model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) Eawag: Swiss Federal Institue of Aquatich Science and Technology
"""

from pynsim import Network


class ReservoirSystem(Network):
    """A reservoir system containing multiple reservoirs. It holds the
    information about the time step length of the model (default: 1 day =
    86400 seconds), the connectivity matrix and the tolerance value for the
    mass balance closure.
    """

    type = 'Network'

    _properties = {'timestep': 86400,
                   }

    def setup(self, t):
        """Build the connectivity matrix and call the setup functions of each
        node and link.
        """
        # Connectivity
        node_names = dict()

        for i, node in enumerate(self.nodes):
            node_names[node.name] = i

        for i, node_from in enumerate(self.nodes):
            for j, node_to in enumerate(self.nodes):
                self.connectivity[i, j] = 0
        for i, link in enumerate(self.links):
            startnode_id = node_names[link.start_node.name]
            endnode_id = node_names[link.end_node.name]
            self.connectivity[startnode_id, endnode_id] = 1
