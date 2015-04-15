#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A sample model to demonstrate memory usage when a PyNSim simulation is run
multiple times within a loop.

Written by Philipp Meier, Eawag, 2015
"""

import sys
import time
import copy

import pandas as pd

from pynsim import Simulator

from agents.agents import RiverNode
from agents.agents import Diversion
from agents.agents import GenericLink
from agents.agents import RiverNetwork

from engines.routing import Routing

from multiprocessing import Process, Queue

from pympler import tracker


def run_simulation(diversion_pos, discharge_data, draw=False, queue=None):
    """Run the simulation based on a given position of diversion nodes.
    A fixed river network structure is assumed here.

    N1
    |
    N2  N4
    |   |
    N3  N5
     \  /
      N6
      |
      N7   N9
      |    |
      N8  N10
      |  /
      N11
      |
      N12
    """

    N1 = RiverNode(x=0, y=7, name='N1')
    N1.dQdx = copy.deepcopy(discharge_data['N1'])
    N2 = RiverNode(x=0, y=6, name='N2')
    N2.dQdx = copy.deepcopy(discharge_data['N2'])
    N3 = RiverNode(x=0, y=5, name='N3')
    N3.dQdx = copy.deepcopy(discharge_data['N3'])
    N4 = RiverNode(x=2, y=6, name='N4')
    N4.dQdx = copy.deepcopy(discharge_data['N4'])
    N5 = RiverNode(x=2, y=5, name='N5')
    N5.dQdx = copy.deepcopy(discharge_data['N5'])
    N6 = RiverNode(x=1, y=4, name='N6')
    N6.dQdx = copy.deepcopy(discharge_data['N6'])
    N7 = RiverNode(x=1, y=3, name='N7')
    N7.dQdx = copy.deepcopy(discharge_data['N7'])
    N8 = RiverNode(x=1, y=2, name='N8')
    N8.dQdx = copy.deepcopy(discharge_data['N8'])
    N9 = RiverNode(x=3, y=3, name='N9')
    N9.dQdx = copy.deepcopy(discharge_data['N9'])
    N10 = RiverNode(x=3, y=2, name='N10')
    N10.dQdx = copy.deepcopy(discharge_data['N10'])
    N11 = RiverNode(x=2, y=1, name='N11')
    N11.dQdx = copy.deepcopy(discharge_data['N11'])
    N12 = RiverNode(x=2, y=0, name='N12')
    N12.dQdx = copy.deepcopy(discharge_data['N12'])

    node_dict = {0: N1, 1: N2, 2: N3, 3: N4, 4: N5, 5: N6, 6: N7, 7: N8, 8: N9,
                 9: N10, 10: N11, 11: N12}

    # Add a diversion node based on the position parameter
    div_node = Diversion(x=node_dict[diversion_pos].x,
                         y=node_dict[diversion_pos].y,
                         name='Diversion')
    div_node.dQdx = node_dict[diversion_pos].dQdx
    div_node.demand = 0.5

    node_dict[diversion_pos] = div_node

    L1 = GenericLink(start_node=node_dict[0], end_node=node_dict[1],
                     name='L1')
    L2 = GenericLink(start_node=node_dict[1], end_node=node_dict[2],
                     name='L2')
    L3 = GenericLink(start_node=node_dict[2], end_node=node_dict[5],
                     name='L3')
    L4 = GenericLink(start_node=node_dict[3], end_node=node_dict[4],
                     name='L4')
    L5 = GenericLink(start_node=node_dict[4], end_node=node_dict[5],
                     name='L5')
    L6 = GenericLink(start_node=node_dict[5], end_node=node_dict[6],
                     name='L6')
    L7 = GenericLink(start_node=node_dict[6], end_node=node_dict[7],
                     name='L7')
    L8 = GenericLink(start_node=node_dict[7], end_node=node_dict[10],
                     name='L8')
    L9 = GenericLink(start_node=node_dict[8], end_node=node_dict[9],
                     name='L9')
    L10 = GenericLink(start_node=node_dict[9], end_node=node_dict[10],
                      name='L10')
    L11 = GenericLink(start_node=node_dict[10], end_node=node_dict[11],
                      name='L11')

    river_network = RiverNetwork(name='River network with diversion')

    river_network.add_nodes(*node_dict.values())
    river_network.add_links(L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11)

    if draw:
        river_network.draw(block=False)

    routing = Routing(river_network)

    simulation = Simulator()
    simulation.network = river_network
    simulation.add_engine(routing)
    simulation.set_timesteps([1])

    simulation.start()

    if queue is None:
        return simulation.network.discharge
    else:
        queue.put(simulation.network.discharge)


if __name__ == '__main__':
    discharge_data = pd.read_csv('data/discharge.csv', header=0,
                                 parse_dates=True)
    discharge_data.columns = [c.strip() for c in discharge_data.columns]

    diversion_positions = range(12)

    print "==================================================================="
    print " Standard loop:"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print
    memory_tracker = tracker.SummaryTracker()
    memory_tracker.print_diff()
    for diversion_pos in diversion_positions:
        st = time.time()
        result = run_simulation(diversion_pos, discharge_data)
        print "Simulation time: %s\n" % (time.time() - st)
        print result
        memory_tracker.print_diff()

    print
    print "==================================================================="
    print " Spawn process in each loop:"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print
    memory_tracker = tracker.SummaryTracker()
    memory_tracker.print_diff()
    for diversion_pos in diversion_positions:
        st = time.time()
        q = Queue()
        p_args = [diversion_pos, discharge_data]
        p_kwargs = dict(queue=q)
        p = Process(target=run_simulation, args=p_args, kwargs=p_kwargs)
        p.start()
        p.join()
        result = q.get()
        print "Simulation time: %s" % (time.time() - st)
        print result
        memory_tracker.print_diff()
