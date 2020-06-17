from .component import Component

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
        ## Check if the new node has an unique name inside the network
        if node.name in self._node_map:
            raise Exception("An node with the name %s is already defined. Node names must be unique."%node.name)

        self.nodes.append(node)
        self.components.append(node)

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
