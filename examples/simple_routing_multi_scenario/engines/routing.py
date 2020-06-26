# -*- coding: utf-8 -*

from pynsim import Engine

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

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
            if node.component_type not in node_types.keys():
                node_types[node.component_type] = [i]
            else:
                node_types[node.component_type].append(i)

        link_types = dict()
        for i, link in enumerate(self.target.links):
            if link.component_type not in link_types.keys():
                link_types[link.component_type] = [i]
            else:
                link_types[link.component_type].append(i)

        # Set initial storage for this simulation time step
        init_stor = dict()
        for res in node_types['Reservoir']:
            # print("self.target.nodes[res]._history")
            # print(self.target.nodes[res]._history)
            if "S" not in self.target.nodes[res]._history or \
                len(self.target.nodes[res]._history['S']) == 0:
                init_stor[res] = self.target.nodes[res].init_stor
                # init_stor[res] = self.target.nodes[res].get_current_history_value("init_stor")

                # print(f"1 - init_stor {res} {init_stor[res]}")
            else:
                # init_stor[res] = self.target.nodes[res]._history['S'][-1]
                init_stor[res] = self.target.nodes[res].get_previous_history_value("S")
                # print(f"2 - init_stor {res} {init_stor[res]}")

        # print(init_stor)
        # input("init_stor")
        # Iteratively calclate releases and storages

        # First calculation of the mass balance:
        for res in node_types['Reservoir']:
            self.target.nodes[res].actual_release = \
                self.target.nodes[res].target_release

        self.update_mass_balance(node_types['Reservoir'], init_stor)
        try:
            maxFlag = [self.target.nodes[res].S - self.target.nodes[res].max_stor
                       > self.target.tol
                       for res in node_types['Reservoir']]
            minFlag = [self.target.nodes[res].min_stor - self.target.nodes[res].S
                       > self.target.tol
                       for res in node_types['Reservoir']]
        except Exception:
            self.target.nodes[res]._simulator.overall_status.dump()
            raise Exception("stop")

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
            sum_total = sum([self.target.nodes[i].actual_release
                           * self.target.connectivity[i, res]
                           for i in nodes])

            try:
                self.target.nodes[res].S = init_stor[res] \
                    + self.target.nodes[res].inflow * self.target.timestep \
                    - self.target.nodes[res].actual_release * self.target.timestep\
                    + sum([self.target.nodes[i].actual_release
                           * self.target.connectivity[i, res]
                           for i in nodes]) * self.target.timestep

            except Exception:
                print(self.target.nodes[res]._simulator.overall_status.dump())
                raise Exception("stop")
