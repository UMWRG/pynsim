from .component import Component, logging, logger

class Node(Component):
    """
        A node represents an individual actor in a network, in water resources
        this is normally a single building or small geogrephical area with
        particular characteristics

        When subclassing a node, if overloading the __setattr__ method, please add the following line at the top of the overloading method


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
