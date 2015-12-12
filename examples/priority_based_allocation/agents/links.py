# -*- coding: utf-8 -*-
"""This file defines all link types needed for the model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) 2014 Eawag: Swiss Federal Institute of Aquatic Science and Technology
"""

from pynsim import Link


class Channel(Link):
    """A channel that transports water at a cost.

    Variables: Q (actual flow)
    Attributes: cost (time series)
                flowmult (time series)
                min_flow (time series)
                max_flow (time series)
    """

    type = 'Channel'
    _properties = {'cost': None,
                   'flowmult': None,
                   'min_flow': None,
                   'max_flow': None,
                   'Q': None,
                   }

    def setup(self, t):
        self.cost = self._cost[t]
        self.flowmult = self._flowmult[t]
        self.min_flow = self._min_flow[t]
        self.max_flow = self._max_flow[t]
