#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementation of a simple model for routing flows through a reservoir
system. Each reservoir has an inflow (from its corresponding watershed) and a
taget release (release decision). The simulation implements this target release
is implemented for each reservoir, while at the same time physical constraints
(mximum and minimum storage )are satisfied. For example, if a reservoir is full
and the target release is smaller than the inflow, the release is adjusted
accordingly.

Network structure:

    (R) : Reservoir
    (J) : Junction
    I   : Inflows


    I--(R1)
        |
        |
    I--(R2)   (R3)--I
         \    /
          \  /
          (R4)--I
            |
            |

The mass balance needs to be closed at each node.

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) 2014 Eawag: Swiss Federal Institute of Aquatic Science and Technology
"""

from pynsim import Simulator
from pynsim import Utilities

from agents.nodes import Reservoir
from agents.links import River
from agents.networks import ReservoirSystem

from engines.routing import SimpleRouting
from os import path
import json
import re

import sys
utils = Utilities()


if len(sys.argv) < 2:
    raise Exception("You must pass the input file name!")

data_file_name = sys.argv[1]
if not path.exists(data_file_name):
    raise Exception(f"The file '{data_file_name}' does not exists!")


simulation_components = {}

# Simulation
simulation = Simulator()


timesteps = utils.get_time_steps(data_file_name)

simulation.set_timesteps(timesteps)

# Network
network = ReservoirSystem(simulator=simulation, name="Example reservoir system")
network.timestep = 86400 * 30  # one month
network.tol = 0.1  # Tolerance value for mass balance error

simulation.network = network

# Creates all components
utils.create_components(
    simulation,
    simulation_components,
    data_file_name, {
        "nodes": [Reservoir],
        "links": [River]
    }
)

# Updates components properties reading the file
utils.update_components_from_file(simulation_components,data_file_name)


engine = SimpleRouting(network)
simulation.add_engine(engine)

simulation.start()

props = ['S', 'actual_release', 'min_stor', 'max_stor', 'init_stor', 'target_release', 'inflow']

# simulation.export_history_multi(props,"./logs/simple-routing")

# Plot results
import seaborn
import matplotlib.pyplot as plt

figure_counter=1
for scenario_item in simulation.get_scenario_manager().get_scenarios_iterator("full"):
    scenario_item_data  = scenario_item["data"]
    scenario_item_index = scenario_item["index"]
    scenario_item_tuple = scenario_item["tuple"]

    local_history={}
    plt.figure(figure_counter)
    for i, node in enumerate(simulation.network.nodes):

        node.set_current_scenario_index_tuple(scenario_item_tuple)

        local_history["S"] = node.get_multi_scenario_history("S")
        local_history["target_release"] = node.get_multi_scenario_history("target_release")
        local_history["actual_release"] = node.get_multi_scenario_history("actual_release")
        local_history["inflow"] = node.get_multi_scenario_history("inflow")

        local_history_dict= node.get_multi_scenario_history_all_properties()

        plt.subplot(2, 4, i + 1)
        plt.plot([timesteps[0], timesteps[-1]], [node.min_stor, node.min_stor], 'r')
        plt.plot([timesteps[0], timesteps[-1]], [node.max_stor, node.max_stor], 'r')
        plt.plot(local_history['S'], 'b')
        plt.ylim([0, node.max_stor])
        plt.xlim([timesteps[0], timesteps[-1]])
        plt.title('R%s storage' % (i + 1))
        plt.subplot(2, 4, i + 5)
        plt.plot(local_history['target_release'], 'r')
        plt.plot(local_history['actual_release'], 'b')
        plt.ylim(ymin=0)
        plt.xlim([timesteps[0], timesteps[-1]])
        plt.title('R%s release' % (i + 1))
        if i == 0:
            plt.legend(['Target release', 'Actual release'])

    figure_counter = figure_counter +1
plt.show()
