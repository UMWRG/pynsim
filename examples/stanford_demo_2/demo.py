from components import UrbanNode, AgriculturalNode, SurfaceReservoir, Junction, RiverSection,StanfordDemoNetwork2
from engines import PyomoAllocation

from pynsim import Simulator, Network

#create the simulator to run
s = Simulator()

timesteps = ["1", "2", "3", "4", "5", "6"]

#add the timesteps to the simulator. The simulator may use these timesteps
#to access timeseries data in the network.
s.set_timesteps(timesteps)

n = StanfordDemoNetwork2(name="demo2+ network")

#Create the surface reservoir with a name, x and y coordinate.
sr1 = SurfaceReservoir(x=1,  y=2,   name="SR1")
#Add internal data to the reservoir. Internal data is signifiied by having an
#underscore before the start of the variable name. 
#The surface reservoir type has an initial storage, inflow, min storage and max storage
#so these are specified here.
sr1._initial_storage =450
sr1._inflow = {
        "1"  : 300,
        "2" : 320,
        "3" : 50,
        "4" : 40,
        "5" : 310,
        "6" : 310,
    }
sr1._min_storage = {
        "1" : 10,
        "2" : 10,
        "3" : 10,
        "4" : 10,
        "5" : 10,
        "6" : 10,
    }
sr1._max_storage = {
        "1" : 500,
        "2" : 500,
        "3" : 500,
        "4" : 500,
        "5" : 500,
        "6" : 500,
    }


#An agricultural node has a cost, demand and consumption coefficient so these values must
#be specified here.
ag1 = AgriculturalNode(x=1,   y=2,   name="Ag1")
ag1._cost = {
        "1" :50, 
        "2" :100, 
        "3" :100, 
        "4" :30, 
        "5" :90, 
        "6" :50, 
    }
ag1._demand = {
        "1" : 55,
        "2" : 100,
        "3" : 150,
        "4" : 195,
        "5" : 100,
        "6" : 29,
    }
ag1._consumption_coefficient = {
        "1" : 1,
        "2" : 1,
        "3" : 1,
        "4" : 1,
        "5" : 1,
        "6" : 1,
    }

#An urban node is another form of demand node, so has a cost, demand and 
#consumption coefficient.
urb1 = UrbanNode(x=10,  y=20,  name="Urb1")
urb1._cost = {
        "1" :100, 
        "2" :100, 
        "3" :100, 
        "4" :100, 
        "5" :50, 
        "6" :500, 
    }
urb1._demand = {
        "1" : 75,
        "2" : 120,
        "3" : 180,
        "4" : 220,
        "5" : 150,
        "6" : 49,
    }
urb1._consumption_coefficient = {
        "1" : 1,
        "2" : 1,
        "3" : 1,
        "4" : 1,
        "5" : 1,
        "6" : 1,
    }

#Junction nodes have no data 
jn1 = Junction(x=100, y=200, name="J1")
endpt = Junction(x=150, y=250, name="Endpt")

#Add the nodes to the network.
n.add_nodes(sr1, urb1, ag1, jn1, endpt)

#Specify link data in dictionaries.
flow_mult_matrix = {
    "l1" : {"1": 1, "2":1, "3":1, "4":1, "5": 1, "6": 1},
    "l2" : {"1": 1, "2":0.9, "3":1, "4":0.95, "5": 1, "6": 1}, 
    "l3" : {"1": 0.95, "2":0.85, "3":0.9, "4":0.85, "5": 0.9, "6": 1}, 
    "l4" : {"1": 1, "2":1, "3":1, "4":1, "5": 1, "6": 1},
}

flow_upper_matrix = {
    "l1" : {"1": 200, "2":210, "3":210, "4":200, "5": 200, "6": 200},
    "l2" : {"1": 310, "2":300, "3":300, "4":300, "5": 310, "6": 300}, 
    "l3" : {"1": 220, "2":250, "3":240, "4":230, "5":240, "6": 250}, 
    "l4" : {"1": 200, "2":200, "3":200, "4":200, "5": 200, "6": 200},
}
flow_lower_matrix = {
    "l1" : {"1": 25, "2":15, "3":10, "4":10, "5": 15, "6": 15},
    "l2" : {"1": 10, "2":10, "3":10, "4":10, "5": 10, "6": 10}, 
    "l3" : {"1": 20, "2":10, "3":25, "4":20, "5":20, "6": 20}, 
    "l4" : {"1": 0, "2":0, "3":0, "4":0, "5": 0, "6": 0},
}

flow_cost_matrix = {
    "l1" : {"1": 20, "2":8, "3":20, "4":15, "5": 19, "6": 10},
    "l2" : {"1": 15, "2":15, "3":15, "4":15, "5": 15, "6": 15},
    "l3" : {"1": 1, "2":10, "3":7, "4":2, "5":3, "6": 5},
    "l4" : {"1": 10, "2":10, "3":10, "4":10, "5": 10, "6": 10},
}

#Create some links and set their data by accessing the above data tables.
#Links have a start node and end node. 
l1 = RiverSection(name="l1", start_node=sr1, end_node=ag1)
l1._flow_multiplier = flow_mult_matrix["l1"]
l1._lower_flow = flow_lower_matrix['l1']
l1._upper_flow = flow_upper_matrix['l1']
l1._cost=flow_cost_matrix['l1']

l2  =RiverSection(name="l2", start_node=sr1, end_node=jn1)
l2._flow_multiplier = flow_mult_matrix["l2"]
l2._lower_flow = flow_lower_matrix['l2']
l2._upper_flow = flow_upper_matrix['l2']
l2._cost=flow_cost_matrix['l2']


l3 = RiverSection(name="l3", start_node=jn1, end_node=urb1)
l3._flow_multiplier = flow_mult_matrix["l3"]
l3._lower_flow = flow_lower_matrix['l3']
l3._upper_flow = flow_upper_matrix['l3']
l3._cost=flow_cost_matrix['l3']


l4 = RiverSection(name="l4", start_node=jn1, end_node=endpt)
l4._flow_multiplier = flow_mult_matrix["l4"]
l4._lower_flow = flow_lower_matrix['l4']
l4._upper_flow = flow_upper_matrix['l4']
l4._cost=flow_cost_matrix['l4']

#When adding these links to the network, the network's nodes will be updated also
#with the link added to the starting node's 'out links' and the ending node's 'in links'
n.add_links(l1, l2, l3, l4)

#Set the network on the simulator
s.network = n


#Create an instance of the pyomo allocator engine.
allocator = PyomoAllocation(n)

#add the engine to the simulator. Multiple engines can be added here. The
#engines will be run sequentially based on the order they were added to the
#simulator
s.add_engine(allocator)

#start the simulator
s.start()

total_deficit = 0

nodes_names=[]
for n in n.nodes:
    nodes_names.append(n.name)
    if n.type == 'irrigation':
        print("%s deficit = %s"%(n.name, n.deficit))
        total_deficit += n.deficit




