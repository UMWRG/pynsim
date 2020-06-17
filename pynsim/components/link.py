from .component import Component

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
