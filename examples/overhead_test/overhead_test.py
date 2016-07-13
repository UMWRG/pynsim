import random
import time
from pynsim import Simulator, Network, Node, Link, Institution, Engine

#Create a simulator object which will be run.
s = Simulator()

#Set the timesteps of the simulator.
timesteps = range(100)
s.set_timesteps(timesteps)

#Create the network with initial data
n = Network(name="example network")

num_nodes = 10000
for node_num in range(num_nodes):
    n.add_node(Node(x=node_num, y=node_num, name="Node number %s"%node_num))

for link_num in range(num_nodes):
    start_node = random.choice(n.nodes)
    #Make sure the start and end node aren't the same
    while True:
        end_node = random.choice(n.nodes)
        if end_node.name != start_node.name:
            break
    n.add_link(Link(name="Link number %s"%link_num, start_node=start_node, end_node=end_node))

num_institutions = 100
for inst_num in range(num_institutions):
    i = Institution(name="Instution Number %s"%inst_num)
    i.add_nodes(*n.nodes)
    n.add_institution(i)

#Set the simulator's network to this network.
s.network = n

class EmptyEngine(Engine):
    def update(self):
        pass

#Create an instance of the deficit allocation engine.
empty_engine = EmptyEngine(n)

#add the engine to the simulator
s.add_engine(empty_engine)

t = time.time()
#start the simulator
s.start()

print "Simulation took: %s"%(time.time() - t)




