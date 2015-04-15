# -*- coding: utf-8 -*-

from pynsim import Node
from pynsim import Link
from pynsim import Network


class RiverNode(Node):
    """Generic river node.
    """

    type = 'RiverNode'
    colour = 'blue'
    _properties = {'Q': None,  # Discharge
                   'dQdx': None,  # Incremental flow
                   }


class Diversion(Node):
    """Node for water abstraction.
    """

    type = 'Diversion'
    colour = 'green'
    _properties = {'Q': None,  # Discharge
                   'dQdx': None,  # Incremental flow
                   'demand': None,  # Water demand
                   'abstraction': None,  # Effective water abstraction
                   }


class GenericLink(Link):

    type = 'Link'
    _properties = {'length': None}


class RiverNetwork(Network):
    """A network holding river and diversion nodes.
    """

    type = 'RiverNetwork'
    _properties = {'discharge': None,  # Mean discharge at the outlet node
                   }
