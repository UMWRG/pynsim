#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementation of a simple model for allocating flows on a hierachical basis.
system. Exogenous imputs are defined (i.e. Hydrological Inflows) as the main decision.
The simulation implements the flow allocations based on fixed policies. There is no optimisation.

Network structure:
Nodes:
    (R) : Reservoir
    (J) : Junction
    (F) : Farm
    (U) : Urban
    (E) : Out of system (Unutilised water)
    I   : Inflows


         (J1)
          |
          |
      I--(J2) 
          /\
         /  \  
  (U1)-(J3) (J4)
        |    |
       (F4) (J5)--(F1)
             |
            (J6)--(F2)
             |
            (J7)--(F3)
             |
            (Out)

          
Water should be allocated according to the following rules.
#J1 E.g. Transfer from source
1	100
2	100
3	100
4	100
5	110
6	120
7	140
8	140
9	140
10	120
11	100
12	100

 
#I Inflow to J2 E.g. hydrological inflow
1	120
2	200
3	300
4	250
5	180
6	200
7	180
8	185
9	200
10	200
11	145
12	280


#J2 Allocation rule (%to each)
  J3  J4
1	50	50
2	50	50
3	65	35
4	65	35
5	70	30
6	70	30
7	65	35
8	65	35
9	65	35
10	65	35
11	65	35
12	65	35

#J3
Allocate following to U1 and remainder to F4
U1 Allocation
1	90
2	100
3	100
4	120
5	140
6	140
7	140
8	140
9	120
10	120
11	100
12	100

#J4
Route to J5

#F1, F2, F3
Farms 1,2,3 can have up to 33% of the water each. 
F2 and F3 can have more if allocation upstream is not utilised.

Agricultural Demand Table
	F1	F2	F3
1	85	65	60
2	80	65	60
3	80	65	65
4	80	70	80
5	60	70	85
6	60	80	85
7	50	90	90
8	50	80	45
9	50	80	60
10	60	80	60
11	65	80	70
12	65	80	70

#J5
Min(33% of J5, F1 demand)
Remainder to J6.

#J6
Min(50% of J6, F2 demand)
Remainder to J7.

#J7
Min(100% of J6, F3 demand)
Remainder to 'E1'.

Written by Stephen Knox <stephen.knox@manchester.ac.uk>
(c) 2014 University of Manchester, Manchester, UK 
"""
from pynsim import Simulator

from agents.nodes import Junction, Urban, Farm
from agents.links import River, Transfer, Pipeline
from agents.networks import ReservoirSystem
from engines.routing import SimpleRouting

timesteps = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
             'jul', 'aug', 'sept', 'oct', 'nov', 'dec']

# Nodes
J1 = Junction(x=2, y=1, name='J1')
J2 = Junction(x=2, y=2, name='J2')
J3 = Junction(x=1, y=3, name='J3')
J4 = Junction(x=3, y=3, name='J4')
J5 = Junction(x=3, y=4, name='J5')
J6 = Junction(x=3, y=5, name='J6')
J7 = Junction(x=3, y=6, name='J7')
U1 = Urban(x=0, y=3, name='U1')
F1 = Farm(x=4, y=4, name='F1')
F2 = Farm(x=4, y=5, name='F2')
F3 = Farm(x=4, y=6, name='F3')
F4 = Farm(x=1, y=4, name='F4')
E1 = Junction(x=3, y=7, name='E1')

# Links
J1_J2 = Transfer(start_node=J1, end_node=J2, name='J1_J2')
J2_J3 = Transfer(start_node=J2, end_node=J3, name='J2_J3')
J2_J4 = Transfer(start_node=J2, end_node=J4, name='J2_J4')
J3_U1 = Pipeline(start_node=J3, end_node=U1, name='J3_U1')
J3_F4 = Pipeline(start_node=J3, end_node=F4, name='J3_F4')
J4_J5 = River(start_node=J4,    end_node=J5, name='J4_J5')
J5_J6 = River(start_node=J5,    end_node=J6, name='J5_J6')
J6_J7 = River(start_node=J6,    end_node=J7, name='J6_J7')
J7_E1 = River(start_node=J7,    end_node=E1, name='J7_E1')
J5_F1 = Pipeline(start_node=J5, end_node=F1, name='J5_F1')
J6_F2 = Pipeline(start_node=J6, end_node=F2, name='J6_F2')
J7_F3 = Pipeline(start_node=J7, end_node=F3, name='J7_F3')


#Please can we re-jig so that months are numbered 1 to 12
# Node data
#J1
J1._inflow = {'jan': 100,
             'feb': 100,
             'mar': 100,
             'apr': 100,
             'may': 110,
             'jun': 120,
             'jul': 140,
             'aug': 140,
             'sept': 140,
             'oct': 120,
             'nov': 100,
             'dec': 100,
            }
              
#J2
J2._inflow = {'jan': 120,
             'feb':  200,
             'mar':  300,
             'apr':  250,
             'may':  180,
             'jun':  200,
             'jul':  180,
             'aug':  185,
             'sept': 200,
             'oct':  200,
             'nov':  245,
             'dec':  280,
            }

#Below PSelby added allocation_priority and _Allocation properties
# but these need formualting

J2._allocation_priority = (J2_J3,J2_J4)
J2._allocation_type = 'pct'
#we could have a rule that if not specified it splits evenly beteen nodes...
#Or if say only one link is specified it splits remainder between remaining links.
J2._allocation = {'jan': (50, 50),
                 'feb':  (50, 50),
                 'mar':  (65, 35),
                 'apr':  (65, 35),
                 'may':  (70, 30),
                 'jun':  (70, 30),
                 'jul':  (65, 35),
                 'aug':  (65, 35),
                 'sept': (65, 35),
                 'oct':  (65, 35),
                 'nov':  (65, 35),
                 'dec':  (65, 35),
                }

#J3 Allocation to U1
J3._allocation_priority = J3_U1
J3._allocation_type = 'vol'
J3._allocation = {'jan': 90, 
                 'feb':  100, 
                 'mar':  100, 
                 'apr':  120, 
                 'may':  140, 
                 'jun':  140, 
                 'jul':  140, 
                 'aug':  140, 
                 'sept': 120, 
                 'oct':  120, 
                 'nov':  100, 
                 'dec':  100, 
                }
#Farm Demands
F1._demand = {'jan': 85, 
             'feb': 80, 
             'mar': 80, 
             'apr': 80, 
             'may': 60, 
             'jun': 60, 
             'jul': 50, 
             'aug': 50, 
             'sept': 50, 
             'oct': 60, 
             'nov': 65, 
             'dec': 65, 
            }
              
F2._demand = {'jan': 65, 
             'feb': 65, 
             'mar': 65, 
             'apr': 70, 
             'may': 70, 
             'jun': 80, 
             'jul': 90, 
             'aug': 80, 
             'sept': 80, 
             'oct': 80, 
             'nov': 80, 
             'dec': 80, 
            }

F3._demand = {'jan': 60, 
             'feb':  60, 
             'mar':  65, 
             'apr':  80, 
             'may':  85, 
             'jun':  85, 
             'jul':  90, 
             'aug':  45, 
             'sept': 60, 
             'oct':  60, 
             'nov':  70, 
             'dec':  70, 
            }
              
#J4

#J5
J5._allocation_priority = J5_F1
J5._allocation_type = 'pct'
J5._allocation = {'jan': 33.333,
                 'feb':  33.333,
                 'mar':  33.333,
                 'apr':  33.333,
                 'may':  33.333,
                 'jun':  33.333,
                 'jul':  33.333,
                 'aug':  33.333,
                 'sept': 33.333,
                 'oct':  33.333,
                 'nov':  33.333,
                 'dec':  33.333,
                }

#J6
J6._allocation_priority = J6_F2
J6._allocation_type = 'pct'
J6._allocation = {'jan': 50.0,
                 'feb':  50.0,
                 'mar':  50.0,
                 'apr':  50.0,
                 'may':  50.0,
                 'jun':  50.0,
                 'jul':  50.0,
                 'aug':  50.0,
                 'sept': 50.0,
                 'oct':  50.0,
                 'nov':  50.0,
                 'dec':  50.0,
                }                  

#J7
J7._allocation_priority = J7_F3
J7._allocation_type = 'pct'
J7._allocation = {'jan': 100.0,
                 'feb':  100.0,
                 'mar':  100.0,
                 'apr':  100.0,
                 'may':  100.0,
                 'jun':  100.0,
                 'jul':  100.0,
                 'aug':  100.0,
                 'sept': 100.0,
                 'oct':  100.0,
                 'nov':  100.0,
                 'dec':  100.0,
                }   

# Network
network = ReservoirSystem(name="Allocation in a river system")
network.add_nodes(J1,J2,J3,J4,J5,J6,J7,U1,F1,F2,F3,F4,E1)
network.add_links(J1_J2,J2_J3,J2_J4,J3_U1,J3_F4,J4_J5,J5_J6,J6_J7,J7_E1,J5_F1,J6_F2,J7_F3
)


network.timestep = 86400 * 30  # one month

# Simulation

simulation = Simulator()

simulation.set_timesteps(timesteps)

simulation.network = network

engine = SimpleRouting(network)
simulation.add_engine(engine)

simulation.start()

for node in simulation.network.nodes:
    print("%s: %s"%(node.name, node._history['inflow'][0]))
simulation.network.plot('inflow')
