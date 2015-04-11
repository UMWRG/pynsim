#    (c) Copyright 2014, University of Manchester
#
#    This file is part of PyNSim.
#
#    PyNSim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNSim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNSim.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os


class Agent(object):
    """
        A top level object, from which Networks, Nodes, Links and Institions
        derive. This object is what a model performs its calculations on.
    """
    pass

class Network(Agent):
    """
        A container for nodes, links and institutions.
    """

    def __init__(self, name, **kwargs):
        pass

class Node(Agent):
    """
        A node represents an individual actor in a network, in water resources
        this is normally a single building or small geogrephical area with
        particular characteristics
    """
    def __init__(self, name, x, y, **kwargs):
        pass


class Link(Agent):
    """
        A link between two nodes.
    """

    def __init__(self, name=None, start_node=None, end_node=None, **kwargs):
        pass

class Institution(Agent):
    """
        An institution represents a body within a network which controlls
        a subset of the nodes and links in some way. Multiple institutions
        are contained in a network and the nodes and links within each
        institution can overlap.

        Technically, an institution is simply a container for nodes and links.
    """
    def __init__(self, name, **kwargs):
        pass
