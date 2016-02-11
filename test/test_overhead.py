import unittest
import time
from pynsim import Simulator, Network, Node, Engine
import json

class EmptyEngine(Engine):
    def run(self):
        pass

class OverheadTest(unittest.TestCase):

    def setUp(self):
        print "Setting Up" 
        start = 10
        multiplier = 10
        range_value = 5

        self.num_timesteps = [start*multiplier**i for i in range(range_value)]
        self.num_nodes = [start*multiplier**i for i in range(range_value)]

        print self.num_timesteps
        print self.num_nodes

        self.result_matrix = {} #2D array for timesteps vs num nodes

        for num_timesteps in self.num_timesteps:
            self.result_matrix[num_timesteps] = {}
            for num_nodes in self.num_nodes:
                self.result_matrix[num_timesteps][num_nodes] = None
                
    def test_overhead(self):
        print "Testing overhead..."

        for num_timesteps in self.num_timesteps:
            for num_nodes in self.num_nodes:
                print "%s timesteps *  %s nodes"%(num_timesteps, num_nodes)
                #Create a simulator object which will be run.
                s = Simulator()

                #Set the timesteps of the simulator.
                timesteps = range(num_timesteps)
                s.set_timesteps(timesteps)

                #Create the network with initial data
                n = Network(name="example network %s nodes %s timesteps"%(num_nodes, num_timesteps))

                for node_num in range(num_nodes):
                    n.add_node(Node(x=node_num, y=node_num, name="Node number %s"%node_num))

                #Set the simulator's network to this network.
                s.network = n

                #Create an instance of the deficit allocation engine.
                empty_engine = EmptyEngine(n)

                #add the engine to the simulator
                s.add_engine(empty_engine)

                t = time.time()
                #start the simulator

                s.start()

                self.result_matrix[num_timesteps][num_nodes] = (time.time()-t)

        overhead_result = open('overhead_result.json', 'w')

        overhead_result.write(json.dumps(self.result_matrix))

def run():
    unittest.main()

if __name__ == '__main__':
    run()  # all tests
