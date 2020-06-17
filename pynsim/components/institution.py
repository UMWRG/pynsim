from .container import Container


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
