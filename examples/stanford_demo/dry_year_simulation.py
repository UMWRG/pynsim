from components import CitrusFarm, VegetableFarm, SurfaceReservoir, RiverSection
from components import WaterDepartment , IrrigationDecisionMaker
from engines import DeficitAllocation

from pynsim import Simulator, Network

#Create a simulator object which will be run.
s = Simulator()

#Set the timesteps of the simulator.
timesteps = ["2014-01-01", "2014-02-01", "2014-03-01", "2014-04-01", "2014-05-01"]
s.set_timesteps(timesteps)

#Create the network with initial data
n = Network(name="example network")

#set some initial data on this network.
n.incoming_water_qty = {"2014-01-01": 10,
              "2014-02-01":22,
              "2014-03-01":35,
              "2014-04-01":22,
              "2014-05-01":10}
#Add nodes to the network

#All nodes have an x, y and name. The surface reservoir also has 'release' which
#can be set on creation or after.
sr1 = SurfaceReservoir(x=1,  y=2,   name="R1", release=100.0)

#Citrus farms and vegetable farms are demand nodes. They use the water supplied
#by the reservoir.
irr1 = CitrusFarm(x=1,   y=2,   name="I1")
irr2 = CitrusFarm(x=10,  y=20,  name="I2")
irr3 = VegetableFarm(x=100, y=200, name="I3")

n.add_nodes(sr1, irr1, irr2, irr3)

#Create some links
n.add_link(RiverSection(start_node=sr1, end_node=irr1))
n.add_link(RiverSection(start_node=sr1, end_node=irr2))
n.add_link(RiverSection(start_node=sr1, end_node=irr3))

#Set the simulator's network to this network.
s.network = n

#Add some institutions (loosely based on the Jordan project)
mow = WaterDepartment("Jordan Ministry of Water")
mow.add_nodes(sr1)
jva = IrrigationDecisionMaker("Jordan Valley Authority")
jva.add_nodes(irr1, irr2, irr3)

n.add_institutions(mow, jva)

#Create an instance of the deficit allocation engine.
allocator = DeficitAllocation(n)

#add the engine to the simulator
s.add_engine(allocator)

#start the simulator
s.start()

#Print the deficit of each node and an overall deficit figure.
total_deficit = 0
for n in n.nodes:
    if n.type == 'irrigation':
        print("%s deficit = %s"%(n.name, n.deficit))
        total_deficit += n.deficit

print("Total deficit: %s"%(total_deficit))


