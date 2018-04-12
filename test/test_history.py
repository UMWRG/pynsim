from pynsim import Simulator, Network, Node, Engine 
import unittest
import random

class HistoryTestNode(Node):
    _properties = {
        'property_dict': {},
        'benchmark': None,
    }


    def setup(self, timestamp):
        self.property_dict["test"] = timestamp
        self.benchmark = random.random() 


class EmptyEngine(Engine):
    def run(self):
        pass

class HistoryTest(unittest.TestCase):

    def test_dict_overwrite(self):
        """
            Test to ensure that dictionaries and other objects contained in history
            are not overwritten by maintaining references to the same objects.
        """
        print("Testing...")
        network = Network("History Test Network")
        network.add_node(HistoryTestNode(x=0, y=0, name="Test Node"))

        s = Simulator()
        s.network = network
        s.timesteps = ['a', 'b', 'c']


        s.start()
        
        assert s.network.nodes[0]._history['property_dict'] == [{'test': 'a'}, {'test': 'b'}, {'test': 'c'}]
        
def run():
    unittest.main()

if __name__ == '__main__':
    run()  # all tests
