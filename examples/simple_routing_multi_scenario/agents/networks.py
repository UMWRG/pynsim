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
                   'tol': 0.1,
                   }

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # This allows to propagate the __init__
        # List of fields that will be managed through the scenario manager
