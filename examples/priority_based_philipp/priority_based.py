#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementation of a simple priority based water allocation model. Based on
on the tutorial model developed for the Hydra GAMS App.

Network structure:

      In---SR---J1---Out
            |    |
            |    |
           IRR  URB

In : Inflow to the system
SR : Surface reservoir
IRR: Irrigation area
URB: Urban water demand
J1 : Junction
Out: Outflow of the system

Flow through each link is associated with a cost (equivalent to the priority of
water allocation).

Written by Philipp Meier <philipp.meier@eawag.ch>
(c) 2014 Eawag: Swiss Federal Institute of Aquatic Science and Technology
"""

from pynsim import Simulator

from agents.nodes import SurfaceReservoir
from agents.nodes import IrrigationNode
from agents.nodes import UrbanDemandNode
from agents.nodes import Junction
from agents.nodes import InAndOut

from agents.links import Channel

from agents.networks import WaterResourcesSystem

from engines.allocation import PriorityBased


timesteps = range(6)

# Define nodes

SR = SurfaceReservoir(x=1, y=1, name="SR")

IRR = IrrigationNode(x=1, y=0, name='IRR')
URB = UrbanDemandNode(x=2, y=0, name='URB')

J1 = Junction(x=2, y=1, name='J1')

In = InAndOut(x=0, y=1, name='In')
Out = InAndOut(x=3, y=1, name='Out')

# Node input data

SR.init_stor = 500.0

SR._min_stor = {0: 10.0,
                1: 10.0,
                2: 10.0,
                3: 10.0,
                4: 10.0,
                5: 10.0,
                }
SR._max_stor = {0: 500.0,
                1: 500.0,
                2: 500.0,
                3: 500.0,
                4: 500.0,
                5: 500.0,
                }

SR._carryover_penalty = {0: 20.0,
                         1: 20.0,
                         2: 20.0,
                         3: 20.0,
                         4: 20.0,
                         5: 20.0,
                         6: 20.0,
                         }

IRR.consumption_coeff = 1

URB.consumption_coeff = 1


# Define links

link1 = Channel(start_node=In, end_node=SR, name='In_SR')
link2 = Channel(start_node=SR, end_node=IRR, name='SR_IRR')
link3 = Channel(start_node=SR, end_node=J1, name='SR_J1')
link4 = Channel(start_node=J1, end_node=URB, name='J1_URB')
link5 = Channel(start_node=J1, end_node=Out, name='J1_Out')

# Link input data

link1._cost = {0: 10.0,
               1: 8.0,
               2: 12.0,
               3: 10.0,
               4: 10.0,
               5: 11.0}

link2._cost = {0: 10.0,
               1: 5.0,
               2: 6.0,
               3: 10.0,
               4: 5.0,
               5: 10.0}

link3._cost = {0: 15.0,
               1: 10.0,
               2: 14.0,
               3: 13.0,
               4: 15.0,
               5: 15.0}

link4._cost = {0: 25.0,
               1: 31.0,
               2: 29.0,
               3: 30.0,
               4: 24.0,
               5: 26.0}

link5._cost = {0: 10.0,
               1: 7.0,
               2: 9.0,
               3: 8.0,
               4: 9.0,
               5: 9.0}

link1._flowmult = {0: 1.0,
                   1: 0.9,
                   2: 1.0,
                   3: 0.9,
                   4: 1.0,
                   5: 1.0}

link2._flowmult = {0: 1.0,
                   1: 1.0,
                   2: 1.0,
                   3: 1.0,
                   4: 1.0,
                   5: 1.0}

link3._flowmult = {0: 1.0,
                   1: 0.9,
                   2: 1.0,
                   3: 0.95,
                   4: 1.0,
                   5: 1.0}

link4._flowmult = {0: 0.95,
                   1: 0.85,
                   2: 0.9,
                   3: 0.85,
                   4: 0.9,
                   5: 1.0}

link5._flowmult = {0: 1.0,
                   1: 1.0,
                   2: 1.0,
                   3: 1.0,
                   4: 1.0,
                   5: 1.0}

link1._min_flow = {0: 10.0,
                   1: 10.0,
                   2: 10.0,
                   3: 10.0,
                   4: 10.0,
                   5: 10.0}

link2._min_flow = {0: 10.0,
                   1: 15.0,
                   2: 10.0,
                   3: 10.0,
                   4: 10.0,
                   5: 15.0}

link3._min_flow = {0: 10.0,
                   1: 10.0,
                   2: 10.0,
                   3: 10.0,
                   4: 10.0,
                   5: 10.0}

link4._min_flow = {0: 10.0,
                   1: 10.0,
                   2: 10.0,
                   3: 10.0,
                   4: 10.0,
                   5: 10.0}

link5._min_flow = {0: 10.0,
                   1: 10.0,
                   2: 10.0,
                   3: 10.0,
                   4: 10.0,
                   5: 10.0}

link1._max_flow = {0: 520.0,
                   1: 500.0,
                   2: 520.0,
                   3: 510.0,
                   4: 500.0,
                   5: 500.0}

link2._max_flow = {0:  90.0,
                   1: 100.0,
                   2: 110.0,
                   3: 100.0,
                   4:  90.0,
                   5: 100.0}

link3._max_flow = {0: 310.0,
                   1: 300.0,
                   2: 300.0,
                   3: 300.0,
                   4: 310.0,
                   5: 300.0}

link4._max_flow = {0: 220.0,
                   1: 250.0,
                   2: 200.0,
                   3: 230.0,
                   4: 240.0,
                   5: 250.0}

link5._max_flow = {0: 30.0,
                   1: 40.0,
                   2: 20.0,
                   3: 30.0,
                   4: 30.0,
                   5: 10.0}


# Define network

network = WaterResourcesSystem(name='Priority based')
network.add_nodes(SR, IRR, URB, J1, In, Out)
network.add_links(link1, link2, link3, link4, link5)

# Run simulation
simulation = Simulator()

simulation.set_timesteps(timesteps)

simulation.network = network

engine = PriorityBased(network)

simulation.add_engine(engine)

simulation.start()

import seaborn
import matplotlib.pyplot as plt

plt.figure(1)
plt.subplot(2, 5, 1)
plt.plot(simulation.network.nodes[0]._history['S'])
plt.title('SR storage')

plt.subplot(2, 5, 2)
plt.plot(simulation.network.nodes[1]._history['delivery'])
plt.title('IRR delivery')

plt.subplot(2, 5, 3)
plt.plot(simulation.network.nodes[2]._history['delivery'])
plt.title('URB delivery')

plt.subplot(2, 5, 4)
plt.plot(simulation.network.nodes[3]._history['Q'])
plt.title('In flow')

plt.subplot(2, 5, 5)
plt.plot(simulation.network.nodes[4]._history['Q'])
plt.title('Out flow')

for i, link in enumerate(simulation.network.links):
    plt.subplot(2, 5, i + 6)
    plt.plot(link._history['Q'])
    plt.title('%s flow' % link.name)

plt.show()

print("Objective: ", sum(simulation.network._history['cost']))
