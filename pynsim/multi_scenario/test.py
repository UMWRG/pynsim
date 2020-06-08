import logging
import numpy as np
import array
import pandas as pd
import uuid
from pynsim.multi_scenario import ScenariosManager


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
        logger.info("get atree {}".format(name))
        return super().__getattr__(name)
        # return self._attributes[name]

    def __setattr__(self, name, value):
        logger.info("set attr {}: {}".format(name, value))
        self._attributes[name] = value
        super().__setattr__(name, value)

logger.info("Initialising MSData")

cp = Component()
cp.test()

cp.a=1
cp.a=2

print(cp.a)


# a = np.array([[{'name':'timestep', 'value':1},{'name':'timestep', 'value':2}], [{'name':'pippo', 'value':2}, {'name':'pippo', 'value':4}, {'name':'pippo', 'value':4}]])
#
# for index, x in np.ndenumerate(a):
#
#     print(index, x)
#     print(range(len(a)))
#     for al in range(len(a)):
#         print(a[al][index[al]])


sm = ScenariosManager()
sm.add_scenario(name={"a":"timesteps"},data=[1,2,3])
sm.add_scenario(name="r1.inflow",data=[10,11,13])
sm.add_scenario(name="r2.inflow",data=[4,5,0,20,21])
sm.add_scenario(name="r2.demand",data=[20,21])
# sm.add_scenario(name="r3.pippo",data=[9,8,7,6,5,4,3,2,1,20,21])
sm.add_scenario(name="r4.pluto",data=999)
sm.add_scenario(name=None,data=111)
# sm.add_scenario(name="r4.minnie",data=[{"nome":12},{"cognome":12}])

for x in sm.get_scenarios_iterator("full"):
    logger.info(x)
    pass

# xx=sm.get_scenarios_iterator("simple")
# #
# for x in xx:
#     logger.info(x)
"""
a. simulator.timesteps is always an array
1 - Esplicity defined in code as a list
2 - Implicity defined using a json range and applied to pandas data type to generate a periodIndex that is a list

b. intercepts the timesteps setting
define an enumerator as N-uple, having the timesteps as first attribute
"""
