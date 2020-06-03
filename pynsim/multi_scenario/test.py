import logging
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

class ScenariosManager(object):
    """
        SM
    """
    _multi_scenario={
        "names":[],
        "values":[],
        "indexes":[]
    }
    def add_scenario(self, name, data):
        self._multi_scenario["names"].append(name)
        self._multi_scenario["values"].append(data)
        self._multi_scenario["indexes"].append(range(len(data)))

    def tuple_iterator(self):
        # returns the iterator of all the scenarios combinations
        print("tuple_iterator")
        iterables = np.array(self._multi_scenario["values"])
        #
        #pd.MultiIndex.from_product(iterables)
        for index in list(pd.MultiIndex.from_product(iterables)):
            yield index

    def indexes_iterator(self):
        # returns the iterator of all the scenarios combinations
        print("indexes_iterator")
        iterables = np.array(self._multi_scenario["indexes"])
        #
        #pd.MultiIndex.from_product(iterables)
        for index in list(pd.MultiIndex.from_product(iterables)):
            yield index



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
sm.add_scenario("timesteps",[1,2,3])
sm.add_scenario("inflow",[10,11,13])
sm.add_scenario("out",[20,21])

for it in sm.tuple_iterator():
    print(it)

for it in sm.indexes_iterator():
    print(it)
"""
a. simulator.timesteps is always an array
1 - Esplicity defined in code as a list
2 - Implicity defined using a json range and applied to pandas data type to generate a periodIndex that is a list

b. intercepts the timesteps setting
define an enumerator as N-uple, having the timesteps as first attribute


"""
