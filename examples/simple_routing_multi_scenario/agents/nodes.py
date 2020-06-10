# -*- coding: utf-8 -*-
"""This file defines node types used in the routing model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) Eawag: Swiss Federal Institue of Aquatich Science and Technology
"""

from pynsim import Node


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # This allows to propagate the __init__
        # List of fields that will be managed through the scenario manager
        self._scenarios_parameters = [
                       'min_stor',
                       'max_Stor',
                       'init_stor',
                       'target_release',
                       'inflow'
                       ]

    def setup(self, t):
        self.target_release = self._target_release[t]
        self.inflow = self._inflow[t]
