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

from agents.nodes import Reservoir
from agents.links import River
from agents.networks import ReservoirSystem

from engines.routing import SimpleRouting

simulation = Simulator()

timesteps = range(12)

# Nodes
R1 = Reservoir(simulator=simulation, x=0, y=2, name='R1')
R2 = Reservoir(simulator=simulation, x=0, y=1, name='R2')
R3 = Reservoir(simulator=simulation, x=2, y=1, name='R3')
R4 = Reservoir(simulator=simulation, x=1, y=0, name='R4')

# Links
L1 = River(simulator=simulation, start_node=R1, end_node=R2, name='R1_R2')
L2 = River(simulator=simulation, start_node=R2, end_node=R4, name='R2_R4')
L3 = River(simulator=simulation, start_node=R3, end_node=R4, name='R3_R4')

# Node data

#R1
R1.max_stor = 1e8
R1.min_stor = 5e6
R1.init_stor = R1.max_stor * 0.8
R1._inflow = {0: 5,
              1: 9,
              2: 10,
              3: 15,
              4: 20,
              5: 22,
              6: 25,
              7: 18,
              8: 16,
              9: 13,
              10: 7,
              11: 6,
              }

R1.add_scenario(
    "inflow",
    {
        0: 5,
        1: 9,
        2: 10,
        3: 15,
        4: 20,
        5: 22,
        6: 25,
        7: 18,
        8: 16,
        9: 13,
        10: 7,
        11: 6,
     })


R1._target_release = {0: 8,
                      1: 8,
                      2: 8,
                      3: 8,
                      4: 18,
                      5: 18,
                      6: 18,
                      7: 18,
                      8: 18,
                      9: 18,
                      10: 8,
                      11: 8,
                      }

# This Reservoir has a multi scenario
# R1._target_release = [{
#                         0: 8,
#                         1: 8,
#                         2: 8,
#                         3: 8,
#                         4: 18,
#                         5: 18,
#                         6: 18,
#                         7: 18,
#                         8: 18,
#                         9: 18,
#                         10: 8,
#                         11: 8,
#                       }, {
#                         0: 6,
#                         1: 6,
#                         2: 6,
#                         3: 6,
#                         4: 16,
#                         5: 16,
#                         6: 16,
#                         7: 16,
#                         8: 16,
#                         9: 16,
#                         10: 2,
#                         11: 2,
#                       }]



#R2
R2.max_stor = 2e8
R2.min_stor = 1e7
R2.init_stor = R2.max_stor * 0.8
R2._inflow = {0: 4,
              1: 6,
              2: 7,
              3: 12,
              4: 17,
              5: 17,
              6: 22,
              7: 15,
              8: 12,
              9: 9,
              10: 6,
              11: 5,
              }

# This Reservoir has a multi scenario
# R2._inflow = [{
#                 0: 4,
#                 1: 6,
#                 2: 7,
#                 3: 12,
#                 4: 17,
#                 5: 17,
#                 6: 22,
#                 7: 15,
#                 8: 12,
#                 9: 9,
#                 10: 6,
#                 11: 5,
#               },{
#                 0: 4,
#                 1: 6,
#                 2: 7,
#                 3: 15,
#                 4: 19,
#                 5: 20,
#                 6: 24,
#                 7: 18,
#                 8: 11,
#                 9: 7,
#                 10: 6,
#                 11: 5,
#             }]
#


R2._target_release = {0: 15,
                      1: 15,
                      2: 25,
                      3: 25,
                      4: 25,
                      5: 25,
                      6: 25,
                      7: 25,
                      8: 25,
                      9: 15,
                      10: 15,
                      11: 15,
                      }

#R3
R3.max_stor = 1e9
R3.min_stor = 1e7
R3.init_stor = R3.max_stor * 0.8
R3._inflow = {0: 4,
              1: 6,
              2: 7,
              3: 12,
              4: 17,
              5: 17,
              6: 22,
              7: 15,
              8: 12,
              9: 9,
              10: 6,
              11: 5,
              }
R3._target_release = {0: 15,
                      1: 15,
                      2: 17,
                      3: 17,
                      4: 20,
                      5: 20,
                      6: 20,
                      7: 20,
                      8: 17,
                      9: 17,
                      10: 15,
                      11: 15,
                      }

#R4
R4.max_stor = 2e8
R4.min_stor = 1e7
R4.init_stor = R4.max_stor * 0.8
R4._inflow = {0: 4,
              1: 6,
              2: 7,
              3: 12,
              4: 17,
              5: 17,
              6: 22,
              7: 15,
              8: 12,
              9: 9,
              10: 6,
              11: 5,
              }
R4._target_release = {0: 45,
                      1: 45,
                      2: 45,
                      3: 55,
                      4: 55,
                      5: 55,
                      6: 65,
                      7: 65,
                      8: 65,
                      9: 45,
                      10: 45,
                      11: 45,
                      }

# Network
network = ReservoirSystem(simulator=simulation, name="Example reservoir system")
network.add_nodes(R1, R2, R3, R4)
network.add_links(L1, L2, L3)

network.timestep = 86400 * 30  # one month
network.tol = 0.1  # Tolerance value for mass balance error

# Simulation



simulation.set_timesteps(timesteps)

simulation.network = network

engine = SimpleRouting(network)

simulation.add_engine(engine)

simulation.start()

# Plot results
import seaborn
import matplotlib.pyplot as plt

plt.figure(1)
for i, node in enumerate(simulation.network.nodes):
    plt.subplot(2, 4, i + 1)
    plt.plot([timesteps[0], timesteps[-1]], [node.min_stor, node.min_stor], 'r')
    plt.plot([timesteps[0], timesteps[-1]], [node.max_stor, node.max_stor], 'r')
    plt.plot(node._history['S'], 'b')
    plt.ylim([0, node.max_stor])
    plt.xlim([timesteps[0], timesteps[-1]])
    plt.title('R%s storage' % (i + 1))
    plt.subplot(2, 4, i + 5)
    plt.plot(node._history['target_release'], 'r')
    plt.plot(node._history['actual_release'], 'b')
    plt.ylim(ymin=0)
    plt.xlim([timesteps[0], timesteps[-1]])
    plt.title('R%s release' % (i + 1))
    if i == 0:
        plt.legend(['Target release', 'Actual release'])

plt.show()
