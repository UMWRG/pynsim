import logging
import numpy as np
import array
import pandas as pd
import uuid
from pynsim.multi_scenario import ScenariosManager
from pynsim.components import Node

from pynsim.simulators import Simulator
simulation = Simulator()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)


class Component(object):
    """
        TEST
    """
    _attributes={}

    def __init__(self):
        logger.info("Initialising MSData")

    def test(self):
        logger.info("Initialising MSData")

    def __getattr__(self, name):
        logger.info("get attr {}".format(name))
        return super().__getattr__(name)
        # return self._attributes[name]

    def __setattr__(self, name, value):
        logger.info("set attr {}: {}".format(name, value))
        self._attributes[name] = value
        super().__setattr__(name, value)

class Reservoir(Node):
    """A surface reservoir with a monthly target release.

    Variables: S (storage)
               actual_release
    Parameters: min_stor
                max_stor
                init_stor
                target_release
                inflow
    """

    _properties = {'S': None,
                   'actual_release': None,
                   'min_stor': None,
                   'max_Stor': None,
                   'init_stor': None,
                   'target_release': None,
                   'inflow': None,
                   }

    _scenarios_parameters = {
        '_target_release':  'target_release',
        '_inflow':          'inflow'
    }

    _internal_status_fields = [ 'S', 'actual_release' ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # This allows to propagate the __init__
        # List of fields that will be managed through the scenario manager

    def setup(self, t):
        self.target_release = self._target_release[t]
        self.inflow = self._inflow[t]






n1 = Reservoir(name="r1", x=10,y=20, simulator=simulation)

n1.S = 100

# n1.add_scenario(type="node", name="r1.inflow",data=[10,11,13])
n1._inflow = {
                0: 11,
                1: 22,
                2: 33,
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

n2 = Reservoir(name="r2", x=10,y=20, simulator=simulation)
n2.max_stor = 1e8
n2.S = 300
n2._inflow = [
                {
                    0: 14,
                    1: 16,
                    2: 17,
                    3: 12,
                    4: 17,
                    5: 17,
                    6: 22,
                    7: 15,
                    8: 12,
                    9: 9,
                    10: 6,
                    11: 5,
                },
                {
                    0: 4,
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
            ]

n2.actual_release = 50

n3 = Reservoir(name="r3", x=10,y=20, simulator=simulation)

n3._inflow = [1,2,3,4]

# logger.info("Initialising MSData")

# cp = Component()
# cp.test()
#
# cp.a=1
# cp.a=2
#
# print(cp.a)


# sm = ScenariosManager()
# sm.add_scenario(type="node", name={"a":"timesteps"},data=[1,2,3])
# sm.add_scenario(type="node", name="r1.inflow",data=[10,11,13])
# sm.add_scenario(type="node", name="r2.inflow",data=[4,5,0,20,21])
# sm.add_scenario(type="node", name="r2.demand",data=[20,21])
# # sm.add_scenario(name="r3.pippo",data=[9,8,7,6,5,4,3,2,1,20,21])
# sm.add_scenario(type="node", name="r4.pluto",data=999)
# sm.add_scenario(type="node", name=None,data=111)
# # sm.add_scenario(name="r4.minnie",data=[{"nome":12},{"cognome":12}])
#
# for x in sm.get_scenarios_iterator("full"):
#     logger.info(x)
#     pass

sm = simulation.get_scenario_manager()
# for x in sm.get_scenarios_iterator("full"):
#      logger.info(x)
#      pass
#
# for x in sm.get_scenarios_iterator("simple"):
#      logger.info(x)
#      #logger.info(sm.get_current_component_property_data("Reservoir","r3","_inflow"))
#      pass
logger.error("FULL")
for x in sm.get_scenarios_iterator("full"):
     logger.info(x)

logger.error("TREE")
for x in sm.get_scenarios_iterator("tree"):
     logger.info(x)
     #logger.info(sm.get_current_component_property_data("Reservoir","r3","_inflow"))
     logger.info(x["data"]["Reservoir"]["r3"]["properties"]["_inflow"]["data"])

logger.error("TREE")
for x in sm.get_scenarios_iterator("tree"):
     logger.info("Full data %s", x)
     for node_type in x["data"]:
         logger.info("node_type %s", node_type)
         for node_name in x["data"][node_type]:
             logger.info("node_name %s", node_name)
         # restore the status of every node
         #node.object_reference.restore_status(x["tuple"])



"""
a. simulator.timesteps is always an array
1 - Esplicity defined in code as a list
2 - Implicity defined using a json range and applied to pandas data type to generate a periodIndex that is a list

b. intercepts the timesteps setting
define an enumerator as N-uple, having the timesteps as first attribute
"""
