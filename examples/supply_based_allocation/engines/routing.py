# -*- coding: utf-8 -*

from pynsim import Engine


class SimpleRouting(Engine):
    """Simple routing class for routing water through a network with resevoirs.
    It is assumed that there is no time delay as the water travels through
    links. This assumption is valid for large time steps.
    """

    name = "Simple supply allocation for a junction & farm network."

    def run(self):
        """Allocation for one time step.
        """
        start_node = None
        #Identify the most up-stream node:
        for node in self.target.nodes:
            if node.in_links == []:
                start_node = node
                break

        self.allocate([start_node])

    def allocate(self, nodes):
        next_level = []
        if len(nodes) > 0:
            for node in nodes:
                if node.component_type == 'Junction':
                    node.consume()
                    node.allocate()
                else:
                    node.consume()

                for l in node.out_links:
                        next_level.append(l.end_node)

            self.allocate(next_level)

