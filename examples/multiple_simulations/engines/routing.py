# -*- coding: utf-8 -*-

from pynsim import Engine


class Routing(Engine):
    """Simple routing engine for network with diversions.
    """

    name = "Simple flow routing."
    target = None

    def update(self):
        # Find head nodes
        head_nodes = []
        outlet_node = None
        for node in self.target.nodes:
            if len(node.upstream_nodes) == 0:
                head_nodes.append(node)
            if len(node.downstream_nodes) == 0:
                outlet_node = node

        while len(head_nodes) > 0:
            h_node = head_nodes.pop(0)
            ds_node = self.mass_balance(h_node)
            while ds_node is not None:
                # This loop terminates if the mass balance cannot be calculated
                # because of missing flows in upstream nodes
                h_node = ds_node
                ds_node = self.mass_balance(h_node)
            # Add the node where we left off to head nodes and jump to the next
            # head node
            if h_node != outlet_node:
                head_nodes.append(h_node)
            else:
                self.target.discharge = h_node.Q.mean()

    def mass_balance(self, node):
        Q_in = node.dQdx
        for us_n in node.upstream_nodes:
            if us_n.Q is None:
                return None
            Q_in += us_n.Q
        node.Q = Q_in

        if node.component_type == 'Diversion':
            abstraction = Q_in
            abstraction[abstraction > node.demand] = node.demand
            node.abstraction = abstraction
            node.Q = Q_in - abstraction
        if len(node.downstream_nodes) == 0:
            return None
        else:
            # In this example each node has exactly one downstream node
            return node.downstream_nodes[0]
