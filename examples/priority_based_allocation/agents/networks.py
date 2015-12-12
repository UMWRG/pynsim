# -*- coding: utf-8 -*-
"""This file defines all node types used in the model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) 2014 Eawag: Swiss Federal Institute of Aquatic Science and Technology
"""

from pynsim import Network


class WaterResourcesSystem(Network):
    """A water resources systems network. Its only property is the total cost
    of allocation (which is minimised during optimisation).

    Variables: cost
    """

    type = 'Network'
    _properties = {'cost': None}

    #def setup(self, t):
    #    super(WaterResourcesSystem, self).setup()
