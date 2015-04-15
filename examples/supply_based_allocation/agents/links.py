# -*- coding: utf-8 -*-
"""This file defines link types used in the routing model.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) Eawag: Swiss Federal Institue of Aquatich Science and Technology
"""

from pynsim import Link


class River(Link):
    """A river which establishes a connection between two reservoirs or a
    junction and a reservoir. No hydrological or hydraulic routing  is
    implemented.
    """

    type = "river"
    _properties = {'flow':0}

class Transfer(Link):
    """
    """

    type = "transfer"
    _properties = {'flow':0}

class Pipeline(Link):
    """
    """

    type = "pipeline"
    _properties = {'flow':0}
