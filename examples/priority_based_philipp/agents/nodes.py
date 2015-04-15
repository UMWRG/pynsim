# -*- coding: utf-8 -*-
"""This file defines all node types used in the model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) 2014 Eawag: Swiss Federal Institute of Aquatic Science and Technology
"""

from pynsim import Node


class SurfaceReservoir(Node):
    """A surface reservoir.

    Variables: S (storage)
    Attributes: min_stor (time series)
                max_stor (time series)
                init_stor (constant)
    """

    type = 'Reservoir'
    _properties = {'min_stor': None,
                   'max_stor': None,
                   'carryover_penalty': None,
                   'init_stor': None,
                   'S': None,
                   }

    def setup(self, t):
        self.min_stor = self._min_stor[t]
        self.max_stor = self._max_stor[t]
        self.carryover_penalty = self._carryover_penalty[t]


class DemandNode(Node):
    """A generic demand node.

    Variables: delivery
    Attributes: consumption_coeff (constant)
    """

    type = 'Demand'
    _properties = {'delivery': None,
                   'consumption_coeff': None,
                   }

    def setup(self, t):
        pass


class IrrigationNode(DemandNode):
    """An irrigation node. Inherits from the generic demand node and doesn't
    add any additional properties.
    """
    pass


class UrbanDemandNode(DemandNode):
    """An urban demand node. Inherits from the generic demand node and doesn't
    add any additional properties.
    """
    pass


class Junction(Node):
    """A generic junction node. This node has no properties and an empty
    setup() function
    """

    type = 'Junction'
    _properties = dict()

    def setup(self, t):
        pass


class InAndOut(Node):
    """A node used as inflow or outflow, where the mass balance is not closed.
    A virtual flow (positive for inflow, negative for outflow) can be assigned
    by the allocation engine.

    Variables: Q
    """

    type = 'InAndOut'
    _properties = {'Q': None}

    def setup(self, t):
        pass
