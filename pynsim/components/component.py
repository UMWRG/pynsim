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


def coroutine(func):
    """Coroutine decorator. Source: 'Python Essential Reference' by D.M Beazley
    """
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.next()
        return g
    return start


class Component(object):
    """
        A top level object, from which Networks, Nodes, Links and Institions
        derive. This object is what a model performs its calculations on.
    """
    name = None
    description = None
    _properties = dict()
    _tmp_properties = dict()
    _history = dict()

    def __init__(self, name, **kwargs):
        self.component_type = self.__class__.__name__
        self.name = name
        self._history = dict()
        self._tmp_properties = dict()

        for k, v in self._properties.items():
            setattr(self, k, v)

        for k in self._properties.keys():
            self._history[k] = []

        for k, v in kwargs.items():
            if k not in self._properties.keys():
                raise Exception("Invalid property %s. Allowed properties are: %s" % (k, self._properties.keys()))

    def get_history(self, attr_name):
        """
            Return a dictionary, keyed on timestep, with each value of the
            attribute at that timestep.
        """
        if self._history.get(attr_name):
            return self._history[attr_name]
        else:
            raise Exception("No history for attribute %s", attr_name)

    def get_properties(self):
        """
            Get all the properties for this component (as defined in _properties)
        """
        properties = dict()
        for k in self._properties.keys():
            properties[k] = getattr(self, k)
        return properties

    def __repr__(self):
        return "Component(name=%s)" % (self.name)

    def pre_process(self):
        """
            Save all the current properties in a temporary structure
            so that they are not lost in this time step.
        """
        for k in self._properties.keys():
            self._tmp_properties[k] = getattr(self, k)

    def setup(self, timestamp):
        """
            Setup function to be overwritten in each component implementation
        """
        pass

    def post_process(self):
        """
            Once all the appropriate values have been set, ensure that the
            values from the previous time step is saved for subsequent use.
        """
        for k in self._tmp_properties.keys():
            self._history[k].append(getattr(self, k))


class Container(Component):
    """
     A container of nodes, links and institutions. The superclass for
     a network and an institution.
    """
    def __init__(self, name, **kwargs):
        super(Container, self).__init__(name, **kwargs)

        self.nodes = []
        self.links = []
        self.institutions = []
        self._node_map = {}
        self._link_map = {}
        self._institution_map = {}

    def add_link(self, link):
        """
            Add a single link to the network.
        """
        self.links.append(link)
        self._link_map[link.name] = link
        link.network = self

    def add_links(self, *args):
        """
            Add multiple links to the network like so:
            net.add_links(link1, link2)
        """
        for l in args:
            self.add_link(l)

    def get_link(self, link_name):
        """
            Get one link, by name. Returns None if link is not found.
        """
        return self._link_map.get(link_name)

    def get_links(self, component_type=None):
        """
            Get all the links in the network of the specified type
        """

        if component_type is None:
            return self.links

        links_of_type = []
        for n in self.links:
            if n.component_type.lower() == component_type.lower():
                links_of_type.append(n)

        return links_of_type

    def add_node(self, node):
        """
            Add a single node to the network
        """
        self.nodes.append(node)
        self._node_map[node.name] = node
        node.network = self

    def add_nodes(self, *args):
        """
            Add multiple nodes to the network, like so:
            net.add_nodes(node1, node2)
        """
        for n in args:
            self.add_node(n)

    def get_node(self, node_name):
        """
            Get a single node, by name. Returs None if node is not found.
        """
        return self._node_map.get(node_name)

    def get_nodes(self, component_type=None):
        """
            Get all the nodes in the network of the specified type
        """

        if component_type is None:
            return self.nodes

        nodes_of_type = []
        for n in self.nodes:
            if n.component_type.lower() == component_type.lower():
                nodes_of_type.append(n)

        return nodes_of_type

    def add_institution(self, institution):
        """
            Add a single institutio to the network.
        """
        self.institutions.append(institution)
        self._institution_map[institution.name] = institution
        institution.network = self

    def add_institutions(self, *args):
        """
            Add multiple institutions to the network, like so:
            net.add_institutions(inst1, inst2)
        """
        for institution in args:
            self.add_institution(institution)

    def get_institution(self, institution_name):
        """
            Get a single institution, by name. Returns None if institution
            is not found.
        """
        return self._institution_map.get(institution_name)

    def get_institutions(self, component_type=None):
        """
            Get all the institutions in the network of the specified type
        """

        if component_type is None:
            return self.institutions

        institutions_of_type = []
        for n in self.institutions:
            if n.component_type.lower() == component_type.lower():
                institutions_of_type.append(n)

        return institutions_of_type

    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, self.name)

class Network(Container):
    """
        A container for nodes, links and institutions.
    """
    base_type = 'network'

    def __init__(self, name, **kwargs):
        super(Network, self).__init__(name, **kwargs)

        self.current_timestep = None

        # Coroutine instances for getting up-/downstream nodes and links
        # These will be initiated if the function is called the first time
        self._us_nodes = None
        self._ds_nodes = None
        self._us_links = None
        self._ds_links = None


    def set_timestep(self, timestamp):
        """
            Set the current timestep in the simulation as an attribute
            on the network.
        """
        self.current_timestep = timestamp

    def setup_institutions(self, timestamp):
        """
            Call the setup function of each of the institutions in the network
            in turn.
        """
        for i in self.institutions:
            try:
                i.setup(timestamp)
            except:
                logging.critical("An error occurred setting up institution %s "
                                 "(timestamp=%s)", i.name, timestamp)

    def setup_links(self, timestamp):
        """
            Call the setup function of each of the links in the network
            in turn.
        """
        for l in self.links:
            try:
                l.setup(timestamp)
            except:
                logging.critical("An error occurred setting up link %s "
                                 "(timestamp=%s)", l.name, timestamp)
                raise

    def setup_nodes(self, timestamp):
        """
            Call the setup function of each of the nodes in the network
            in turn.
        """
        for n in self.nodes:
            try:
                n.setup(timestamp)
            except:
                logging.critical("An error occurred setting up node %s"
                                 " (timestamp=%s)", n.name, timestamp)
                raise

    def pre_process(self):
        """
            Pre-process the entire network. This is run before the setup
            function, and saves the current attribute values into a temporary
            state.
        """
        super(Network, self).pre_process()
        for i in self.institutions:
            i.pre_process()

        for l in self.links:
            l.pre_process()

        for n in self.nodes:
            n.pre_process()

    def post_process(self):
        """
            Post process the entire network. Saves any properties to history.
        """
        super(Network, self).post_process()
        for i in self.institutions:
            i.post_process()

        for l in self.links:
            l.post_process()

        for n in self.nodes:
            n.post_process()

    @property
    def connectivity(self):
        """
            Return a dictionary representing the connectivity matrix of the
            network.
        """
        connectivity = dict()

        # Connectivity
        node_names = dict()

        for i, node in enumerate(self.nodes):
            node_names[node.name] = i

        for i, node_from in enumerate(self.nodes):
            for j, node_to in enumerate(self.nodes):
                connectivity[i, j] = 0

        for i, link in enumerate(self.links):
            startnode_id = node_names[link.start_node.name]
            endnode_id = node_names[link.end_node.name]
            connectivity[startnode_id, endnode_id] = 1

        return connectivity

    def draw(self, block=True):
        """
            Draw the pynsim network as a matplotlib plot.
        """
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
            g = nx.Graph()
            #Nodes
            pos = {}
            labels = {}
            for n in self.nodes:
                g.add_node(n)
                pos[n] = (n.x, n.y)
                labels[n] = n.name
            colours = [n.colour for n in g.nodes()]
            nx.draw_networkx_nodes(g, pos, width=8, alpha=0.5,
                                   node_color=colours)
            nx.draw_networkx_labels(g, pos, labels, font_size=10)
            #links
            for l in self.links:
                g.add_edge(l.start_node, l.end_node, name=l.name,
                           colour=l.colour)
            colours = [g[a][b]['colour'] for a, b in g.edges()]

            nx.draw_networkx_edges(g,pos, width=2,alpha=0.5,edge_color=colours)
            mng = plt.get_current_fig_manager()
            mng.resize(1000, 700)
            plt.show(block=block)

        except ImportError, e:
            logging.critical("Cannot draw network. Please ensure matplotlib "
                             "and networkx are installed.")

    def plot(self, property_name, block=True):
        """
            Plot the history of a property
            :param The name of the property to be plotted.
            :param The type of nodes to which this property belongs. 
                   If this is empty, all nodes and links in the network 
                   will be checked for this property.
            :param Stop the current process while displaying the plot. False
                   to continue the process. If false, make sure the process does not
                   end of its own accord (by putting in a request for user input, for example)
                   as the plot will disappear.
        """
        #Import seaborn to prettify the graphs if possible 
        try:
            import seaborn
        except:
            pass

        try:
            import matplotlib.pyplot as plt
            nodes_to_plot = []
            links_to_plot = []
            institutions_to_plot = []
            for n in self.nodes:
                if property_name in n._properties:
                    nodes_to_plot.append(n)
            for l in self.links:
                if property_name in l._properties:
                    if len(nodes_to_plot) > 0:
                        print "WARNING: Some nodes have the same property %s as this link %s"% (property_name, l.name)
                    links_to_plot.append(l)
            for i in self.institutions:
                if property_name in i._properties:
                    if len(nodes_to_plot) > 0 or len(links_to_plot) > 0:
                        print "WARNING: Some nodes and links have the same property %s as this institution (%s)"% (property_name, i.name)
                    institutions_to_plot.append(i)
            
            components_to_plot = nodes_to_plot + links_to_plot + institutions_to_plot

            if len(components_to_plot) == 0:
                print "No components found with property %s"%property_name
                return

            num_cols = 7
            num_rows = (len(components_to_plot) / 7) + 1
            plt.figure(1)
            for i, component in enumerate(components_to_plot):
                plt.subplot(num_rows, num_cols, i + 1)
                plt.plot(component._history[property_name], 'r')
                plt.title('%s' % (component.name))
            plt.show()


        except ImportError, e:
            logging.critical("Cannot plot %s. Please ensure matplotlib "
                             "and networkx are installed."%property_name)



    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, self.name)

    def as_csv(self, target_dir):
        """
            Convert network into a set of hydra-compatible csv files.
        """

        raise NotImplementedError("Not implemented yet.")

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        #create target_dir/network.csv
        net_file = open(os.path.join(target_dir, 'network.csv'))
        #create target_dir/nodes.csv
        node_file = open(os.path.join(target_dir, 'nodes.csv'))
        #create target_dir/links.csv
        link_file = open(os.path.join(target_dir, 'links.csv'))
        #create target_dir/groups.csv
        group_file = open(os.path.join(target_dir, 'groups.csv'))
        #create target_dir/group_members.csv
        group_member_file = open(os.path.join(target_dir, 'group_members.csv'))

    @coroutine
    def _get_upstream_nodes(self):
        """Get a list of nodes upstream of a node.
        Usage: usnodes = network.get_upstream_nodes()
               upstream_nodes = usnodes.send(node)
        """
        _upstream_index = dict()
        node = None
        while True:
            if node in _upstream_index.keys():
                us_nodes = _upstream_index[node]
            else:
                us_nodes = []
                for link in self.links:
                    if link.end_node == node:
                        us_nodes.append(link.start_node)
                _upstream_index[node] = us_nodes
            node = (yield us_nodes)

    @coroutine
    def _get_downstream_nodes(self):
        """Get a list of nodes downstream of a node.
        Usage: dsnodes = network.get_downstream_nodes()
               downstream_nodes = dsnodes.send(node)
        """
        _downstream_index = dict()
        node = None
        while True:
            if node in _downstream_index.keys():
                ds_nodes = _downstream_index[node]
            else:
                ds_nodes = []
                for link in self.links:
                    if link.start_node == node:
                        ds_nodes.append(link.end_node)
                _downstream_index[node] = ds_nodes
            node = (yield ds_nodes)

    @coroutine
    def _get_upstream_links(self):
        """Get a list of links upstream of a node.
        Usage: uslinks = network.get_upstream_links()
               upstream_links = uslinks.send(node)
        """
        _upstream_link_index = dict()
        node = None
        while True:
            if node in _upstream_link_index.keys():
                us_links = _upstream_link_index[node]
            else:
                us_links = []
                for link in self.links:
                    if link.end_node == node:
                        us_links.append(link)
                _upstream_link_index[node] = us_links
            node = (yield us_links)

    @coroutine
    def _get_downstream_links(self):
        """Get a list of links downstream of a node.
        Usage: dslinks = network.get_downstream_links()
               downstream_links = dslinks.send(node)
        """
        _downstream_link_index = dict()
        node = None
        while True:
            if node in _downstream_link_index.keys():
                ds_links = _downstream_link_index[node]
            else:
                ds_links = []
                for link in self.links:
                    if link.end_node == node:
                        ds_links.append(link)
                _downstream_link_index[node] = ds_links
            node = (yield ds_links)


class Node(Component):
    """
        A node represents an individual actor in a network, in water resources
        this is normally a single building or small geogrephical area with
        particular characteristics
    """
    #This never changes
    base_type='node'
    #This is updated in the __init__ function to the name of the node subclass
    component_type = 'node'
    network = None
    colour = 'red'

    def __init__(self, name, x, y, **kwargs):
        super(Node, self).__init__(name, **kwargs)
        self.x = x
        self.y = y
        self.in_links = []
        self.out_links = []

    def __repr__(self):
        return "%s(name=%s, x=%s, y=%s)" % (self.__class__.__name__,
                                            self.name, self.x, self.y)

    @property
    def upstream_nodes(self):
        """Returns a list of all nodes which are *upstream* of the node
        (nodes from where a link leads to this node).
        """
        if self.network._us_nodes is None:
            # initialise if not done already
            self.network._us_nodes = self.network._get_upstream_nodes()
        return self.network._us_nodes.send(self)

    @property
    def downstream_nodes(self):
        """Returns a list of all nodes which are *downstream* of the node
        (nodes to which a link leads).
        """
        if self.network._ds_nodes is None:
            # initialise if not done already
            self.network._ds_nodes = self.network._get_downstream_nodes()
        return self.network._ds_nodes.send(self)

    @property
    def upstream_links(self):
        """Returns a list of links whose end node is this node.
        """
        if self.network._us_links is None:
            # initialise if not done already
            self.network._us_links = self.network._get_upstream_links()
        return self.network._us_links.send(self)

    @property
    def downstream_links(self):
        """Returns a list of links whose start node is this node.
        """
        if self.network._ds_links is None:
            # initialise if not done already
            self.network._ds_links = self.network._get_downstream_links()
        return self.network._ds_links.send(self)


class Link(Component):
    """
        A link between two nodes.
    """
    #this never changes
    base_type='link'
    #This is updated in the __init__ function to the name of the link subclass
    component_type = 'link'
    network = None
    colour = 'black'

    def __init__(self, name=None, start_node=None, end_node=None, **kwargs):
        super(Link, self).__init__(name, **kwargs)
        self.start_node = start_node
        self.end_node = end_node

        start_node.out_links.append(self)
        end_node.in_links.append(self)

    def __repr__(self):
        return "%s(name=%s, start_node=%s, end_node=%s)" % \
            (self.__class__.__name__, self.name, self.start_node.name,
             self.end_node.name)


class Institution(Container):
    """
        An institution represents a body within a network which controlls
        a subset of the nodes and links in some way. Multiple institutions
        are contained in a network and the nodes and links within each
        institution can overlap.

        Technically, an institution is simply a container for nodes and links.
    """
    #THis never changes
    base_type='institution'
    #This is updated in the __init__ function to be the name of the class
    #of the institution
    component_type = 'institution'
    network = None

    def __init__(self, name, **kwargs):
        super(Institution, self).__init__(name, **kwargs)

