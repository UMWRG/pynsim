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
import time

class Component(object):
    """
        A top level object, from which Networks, Nodes, Links and Institions
        derive. This object is what a model performs its calculations on.
    """
    name = None
    description = None
    base_type = 'component'
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
            self._history[k] = []

        for k, v in kwargs.items():
            if k not in self._properties:
                raise Exception("Invalid property %s. Allowed properties are: %s" % (k, self._properties.keys()))

    def get_history(self, attr_name=None):
        """
            Return a dictionary, keyed on timestep, with each value of the
            attribute at that timestep.
        """
        if attr_name is None:
            return self._history
        else:
            return self._history.get(attr_name, None)

    def reset_history(self):
        """
            Reset the _history dict. This is uesful if a simulator instance is
            used for multiple simulations.
        """
        for k in self._properties:
            self._history[k] = []

    def get_properties(self):
        """
            Get all the properties for this component (as defined in
            _properties)
        """
        properties = dict()
        for k in self._properties:
            properties[k] = getattr(self, k)
        return properties

    def __repr__(self):
        return "Component(name=%s)" % (self.name)

    def setup(self, timestamp):
        """
            Setup function to be overwritten in each component implementation
        """
        pass


class Container(Component):
    """
     A container of nodes, links and institutions. The superclass for
     a network and an institution.
    """
    def __init__(self, name, **kwargs):
        #Allow 'nodes' 'links' and 'instutions' to be special case keywords
        nodes = kwargs.get('nodes', [])
        if nodes:
            del kwargs['nodes']
        links = kwargs.get('links', [])
        if links:
            del kwargs['links']
        institutions = kwargs.get('institutions', [])
        if institutions:
            del kwargs['institutions']

        super(Container, self).__init__(name, **kwargs)

        self.components = []
        self.nodes = []
        self.links = []
        self.institutions = []
        self._node_map = {}
        self._link_map = {}
        self._institution_map = {}
        self._component_map = {}
        self._node_type_map = {}
        self._link_type_map = {}
        self._institution_type_map = {}

        self.add_nodes(*nodes)
        self.add_links(*links)
        self.add_institutions(*institutions)

    def add_link(self, link):
        """
            Add a single link to the network.
        """

        if link.start_node is None:
            raise Exception("A link must have a start node")
        if link.end_node is None:
            raise Exception("A link must have an end node")
        if link.name is None:
            default_link_name = link.start_node.name + " . " + link.end_node.name
            link.name = default_link_name
            logging.debug("No link name specified, defaulting to:%s", link.name)

        self.links.append(link)
        self.components.append(link)

        if link.name in self._link_map:
            raise Exception("An link with the name %s is already defined. Link names must be unique."%link.name)

        self._link_map[link.name] = link

        if self.base_type == 'network':
            self.timing['links'][link.name] = 0
            link.network = self

        links_of_type = self._link_type_map.get(link.component_type, [])
        links_of_type.append(link)
        self._link_type_map[link.component_type] = links_of_type


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
            Get all the links in the network of the specified type. If no type
            is specified, return all links.
        """

        if component_type is None:
            return self.links
        else:
            return self._link_type_map.get(component_type, [])

    def add_node(self, node):
        """
            Add a single node to the network
        """
        self.nodes.append(node)
        self.components.append(node)

        if node.name in self._node_map:
            raise Exception("An node with the name %s is already defined. Node names must be unique."%node.name)

        self._node_map[node.name] = node

        #If i'm a network, as opposed to an institution
        if self.base_type == 'network':
            self.timing['nodes'][node.name] = 0
            node.network = self

        nodes_of_type = self._node_type_map.get(node.component_type, [])
        nodes_of_type.append(node)
        self._node_type_map[node.component_type] = nodes_of_type


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
            Get all the nodes in the network of the specified type. If no type
            is specified, return all the nodes.
        """

        if component_type is None:
            return self.nodes
        else:
            return self._node_type_map.get(component_type, [])

    def add_institution(self, institution):
        """
            Add a single institutio to the network.
        """
        self.institutions.append(institution)
        self.components.append(institution)

        if institution.name in self._institution_map:
            raise Exception("An institution with the name %s is already defined. Institutions names must be unique."%institution.name)

        self._institution_map[institution.name] = institution

        #If i'm a network, as opposed to an institution
        if self.base_type == 'network':
            self.timing['institutions'][institution.name] = 0
            institution.network = self

        institutions_of_type = \
            self._institution_type_map.get(institution.component_type, [])
        institutions_of_type.append(institution)
        self._institution_type_map[institution.component_type] = \
            institutions_of_type


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
            Get all the institutions in the network of the specified type. If
            no type is specified, return all the institutions.
        """

        if component_type is None:
            return self.institutions
        else:
            return self._institution_type_map.get(component_type, [])

    def add_component(self, component):
        """
            Add a single component to the network.
        """

        self.components.append(component)

        if component.name in self._component_map:
            raise Exception("An component with the name %s is already defined. Component names must be unique."%component.name)

        self._component_map[component.name] = component

        #If i'm a network, as opposed to a component, then setup timing parameters, and set
        #the network parameter
        if self.base_type == 'network':
            self.timing['unknown'][component.name] = 0
            component.network = self

    def add_components(self, *args):
        """
            Add multiple generic components to the network, like so:
            net.add_components(inst1, inst2)
        """
        for component in args:
            self.add_component(component)


    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, self.name)


class Network(Container):
    """
        A container for nodes, links and institutions.
    """
    base_type = 'network'

    def __init__(self, name, **kwargs):
        super(Network, self).__init__(name, **kwargs)

        #Track the timing of the setup functions for each node,link and institution
        self.timing = {'nodes':{}, 'links':{}, 'institutions':{}, 'unknown':{}}

        self.current_timestep = None
        self.current_timestep_idx = None

    def set_timestep(self, timestamp, timestep_idx):
        """
            Set the current timestep in the simulation as an attribute
            on the network.
        """
        self.current_timestep = timestamp
        self.current_timestep_idx = timestep_idx

    def setup_components(self, timestamp, record_time=False):
        """
            Call the setup function of each of the nodes in the network
            in turn.

            :returns The time it took to call the function (in seconds)
        """

        time_dict = {'nodes':0, 'links':0, 'institutions':0, 'unknown':0}

        for k in self._properties:
            self._history[k].append(getattr(self, k))



        for c in self.components:
            #removed the component's 'pre_process' function for efficiency
            for k in c._properties:
                c._history[k].append(getattr(c, k))

            try:

                if record_time is True:
                    individual_time = time.time()
                
                c.setup(timestamp)

                for k in self._tmp_properties:
                    self._history[k].append(getattr(self, k))

                if record_time is True:
                    #Compile the timing dictionary
                    setup_time = time.time()-individual_time
                    if c.base_type == 'node':
                        self.timing['nodes'][c.name] += setup_time
                        time_dict['nodes'] += setup_time
                    elif c.base_type == 'link':
                        self.timing['links'][c.name] += setup_time
                        time_dict['links'] += setup_time
                    elif c.base_type == 'institution':
                        self.timing['institutions'][c.name] += setup_time
                        time_dict['institutions'] += setup_time
                    elif c.base_type == 'component':
                        self.timing['unknown'][c.name] += setup_time
                        time_dict['unknown'] += setup_time
            except:
                logging.critical("An error occurred setting up node %s"
                                 " (timestamp=%s)", c.name, timestamp)
                raise

        return time_dict

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

            nx.draw_networkx_edges(g, pos, width=2, alpha=0.5,
                                   edge_color=colours)
            mng = plt.get_current_fig_manager()
            mng.resize(1000, 700)
            plt.show(block=block)

        except ImportError, e:
            logging.critical("Cannot draw network. Please ensure matplotlib "
                             "and networkx are installed.")


    def plot_timing(self, component):
        """
         Plot the total time taken to run the setup function of the
         components in the network.

         :param one of the following: 'nodes', 'links', 'institutions'
        """
        #Import seaborn to prettify the graphs if possible
        try:
            import seaborn
        except:
            pass

        try:
            import matplotlib.pyplot as plt

            width = 0.35

            s = self.timing[component].values()
            labels = self.timing[component].keys()
            t = range(len(s)) #Make a list [0, 1, 2...len(s)]
            pos = []
            for x in t:
                pos.append(x+0.15)

            fig, ax = plt.subplots()

            rects1 = ax.bar(t, s, width, color='r')
            ax.set_xticks(pos)
            ax.set_xticklabels(labels)
            ax.set_ylabel('Time')
            plt.title('Timing')

            plt.show(block=True)

        except ImportError, e:
            logging.critical("Cannot plot. Please ensure matplotlib "
                             "and networkx are installed.")

    def plot(self, property_name, block=True):
        """
            Plot the history of a property
            :param The name of the property to be plotted.
            :param The type of nodes to which this property belongs.
                   If this is empty, all nodes and links in the network
                   will be checked for this property.
            :param Stop the current process while displaying the plot. False
                   to continue the process. If false, make sure the process
                   does not end of its own accord (by putting in a request for
                   user input, for example) as the plot will disappear.
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
                if property_name in n.get_properties():
                    nodes_to_plot.append(n)
            for l in self.links:
                if property_name in l.get_properties():
                    if len(nodes_to_plot) > 0:
                        logging.warn("WARNING: Some nodes have the same property %s as this link %s"% (property_name, l.name))
                    links_to_plot.append(l)
            for i in self.institutions:
                if property_name in i.get_properties():
                    if len(nodes_to_plot) > 0 or len(links_to_plot) > 0:
                        logging.warn("WARNING: Some nodes and links have the same property %s as this institution (%s)"% (property_name, i.name))
                    institutions_to_plot.append(i)

            components_to_plot = nodes_to_plot + links_to_plot + \
                institutions_to_plot

            if len(components_to_plot) == 0:
                logging.warn("No components found with property %s"%property_name)
                return

            num_cols = 7
            num_rows = (len(components_to_plot) / 7) + 1
            plt.figure(1)
            for i, component in enumerate(components_to_plot):
                plt.subplot(num_rows, num_cols, i + 1)
                plt.plot(component._history[property_name], 'r')
                plt.title('%s' % (component.name))
            plt.show(block=block)

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


class Node(Component):
    """
        A node represents an individual actor in a network, in water resources
        this is normally a single building or small geogrephical area with
        particular characteristics
    """
    #This never changes
    base_type = 'node'
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
        return [link.start_node for link in self.in_links]

    @property
    def downstream_nodes(self):
        """Returns a list of all nodes which are *downstream* of the node
        (nodes to which a link leads).
        """
        return [link.end_node for link in self.out_links]

    @property
    def upstream_links(self):
        """Returns a list of links whose end node is this node.
        NOTE: This function exists for compatibility and might be removed in
              later releases.
        """
        return self.in_links

    @property
    def downstream_links(self):
        """Returns a list of links whose start node is this node.
        NOTE: This function exists for compatibility and might be removed in
              later releases.
        """
        return self.out_links


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

