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
                   'max_stor': None,
                   'init_stor': None,
                   'target_release': None,
                   'inflow': None,
                   }

    _scenario_parameters = {
        '_target_release':  'target_release',
        '_inflow':          'inflow'
    }

    def setup(self, t):
        self.target_release = self._target_release[str(t)]
        self.inflow = self._inflow[str(t)]
