# -*- coding: utf-8 -*

from pynsim import Engine


class SimpleRouting(Engine):
    """Simple routing class for routing water through a network with resevoirs.
    It is assumed that there is no time delay as the water travels through
    links. This assumption is valid for large time steps.
    """

    name = "Simple flow routing for reservoir network."
    target = None

    def run(self):
        """Flow routing for one time step.
        """

        # Create indices on nodes and links
        node_types = dict()

        for i, node in enumerate(self.target.nodes):
            if node.type not in node_types.keys():
                node_types[node.type] = [i]
            else:
                node_types[node.type].append(i)

        link_types = dict()
        for i, link in enumerate(self.target.links):
            if link.type not in link_types.keys():
                link_types[link.type] = [i]
            else:
                link_types[link.type].append(i)

        # Set initial storage for this simulation time step
        init_stor = dict()
        for res in node_types['Reservoir']:
            if len(self.target.nodes[res]._history['S']) == 0:
                init_stor[res] = self.target.nodes[res].init_stor
            else:
                init_stor[res] = self.target.nodes[res]._history['S'][-1]

        # Iteratively calclate releases and storages

        # First calculation of the mass balance:
        for res in node_types['Reservoir']:
            self.target.nodes[res].actual_release = \
                self.target.nodes[res].target_release

        self.update_mass_balance(node_types['Reservoir'], init_stor)

        maxFlag = [self.target.nodes[res].S - self.target.nodes[res].max_stor
                   > self.target.tol
                   for res in node_types['Reservoir']]
        minFlag = [self.target.nodes[res].min_stor - self.target.nodes[res].S
                   > self.target.tol
                   for res in node_types['Reservoir']]

        # Iterate until the mass balance is satisfied (this iteration could
        # also be replaced by an optimisation algorithm, e.g using pyomo)
        while any(maxFlag) or any(minFlag):
            for i, res in enumerate(node_types['Reservoir']):
                if maxFlag[i]:
                    excess_stor = self.target.nodes[res].S - \
                        self.target.nodes[res].max_stor
                    added_release = excess_stor / self.target.timestep
                    self.target.nodes[res].actual_release += added_release

                elif minFlag[i]:
                    deficit_stor = self.target.nodes[res].S - \
                        self.target.nodes[res].min_stor
                    subtr_release = deficit_stor / self.target.timestep
                    self.target.nodes[res].actual_release += subtr_release

            # Update system storages
            self.update_mass_balance(node_types['Reservoir'], init_stor)

            # Update flags
            maxFlag = [self.target.nodes[res].S
                       - self.target.nodes[res].max_stor
                       > self.target.tol
                       for res in node_types['Reservoir']]
            minFlag = [self.target.nodes[res].min_stor
                       - self.target.nodes[res].S
                       > self.target.tol
                       for res in node_types['Reservoir']]

    def update_mass_balance(self, nodes, init_stor):
        "Calculate the mass balance for all nodes"
        for res in nodes:
            self.target.nodes[res].S = init_stor[res] \
                + self.target.nodes[res].inflow * self.target.timestep \
                - self.target.nodes[res].actual_release * self.target.timestep\
                + sum([self.target.nodes[i].actual_release
                       * self.target.connectivity[i, res]
                       for i in nodes]) * self.target.timestep
