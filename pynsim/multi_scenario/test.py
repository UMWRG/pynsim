import logging
import numpy as np
import array
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)


def is_array_like(obj, string_is_array=False, tuple_is_array=True):
    result = hasattr(obj, "__len__") and hasattr(obj, '__getitem__')
    if result and not string_is_array and isinstance(obj, (str, abc.ByteString)):
        result = False
    if result and not tuple_is_array and isinstance(obj, tuple):
        result = False
    return result

class MultiIndexedData(object):
    """
        This class allows to enumerate all the data combinations in a lazy style.
        Every combination is built upon its request by the client
    """
    _data=[]
    _indexes=[]
    _iteration_finished=False
    def add_data(self, data):
        # data can be an array or a single value
        if not isinstance(data, (list,array,range,np.ndarray)):
            self._data.append([data])
        else:
            self._data.append(data)
        self._indexes.append(0)

        # print(self._data)
        # print(self._indexes)

    def get_next_data(self):
        next_index = self.get_next_index()
        next_data = []
        for col_count, index in enumerate(next_index):
            # print(f"col_count {col_count}, index: {index}")
            next_data.append(self._data[col_count][index])

        return next_data

    def get_next_index(self):
        # Returns the first not used index
        # for datum in self._data
        if self._iteration_finished:
            raise Exception("Data finished")
        _new_index=[]
        flag_update_index_done = False

        _new_index=self._indexes.copy()

        for main_list_index, datum  in reversed(list(enumerate(self._data))):
            # print(f"datum {datum}")
            # print(f"main_list_index {main_list_index}")
            datum_length=len(datum)
            current_datum_index=self._indexes[main_list_index]

            # print(f"datum_length: {datum_length} current_datum_index: {current_datum_index}")

            if flag_update_index_done is False:
                # I have to check the current index
                if current_datum_index < ( datum_length - 1 ):
                    # Increment the index for that column
                    self._indexes[main_list_index] = self._indexes[main_list_index] + 1
                    flag_update_index_done = True
                    break
                else:
                    # Column index overflow
                    self._indexes[main_list_index] = 0

        self._iteration_finished = not flag_update_index_done

        return _new_index

class ScenariosManager(object):
    """
        SM
    """
    _multi_scenario={
        "names":[],
        "values":[],
        "indexes":[]
    }
    _multi_id=None
    def __init__(self):
        self._multi_id = MultiIndexedData()
        print("done")


    def get_next_index(self):
        return self._multi_id.get_next_index()

    def get_next_data(self):
        out_data = []
        for i,item in enumerate(self._multi_id.get_next_data()):
            out_data.append({"name" : self._multi_scenario["names"][i], "value": item})
        return out_data

    def add_scenario(self, name, data):
        self._multi_scenario["names"].append(name)
        self._multi_scenario["values"].append(data)
        self._multi_scenario["indexes"].append(range(len(data)))

        self._multi_id.add_data(data)

    def tuple_iterator(self):
        # returns the iterator of all the scenarios combinations
        print("tuple_iterator")
        iterables = np.array(self._multi_scenario["values"])
        print (iterables)
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
sm.add_scenario("r1.inflow",[10,11,13])
sm.add_scenario("r2.inflow",[4,5,0,20,21])
sm.add_scenario("r2.demand",[20,21])

for it in sm.tuple_iterator():
    print(it)

for it in sm.indexes_iterator():
    print(it)


# print (sm.get_next_index())
while True:
    print (sm.get_next_data())
"""
a. simulator.timesteps is always an array
1 - Esplicity defined in code as a list
2 - Implicity defined using a json range and applied to pandas data type to generate a periodIndex that is a list

b. intercepts the timesteps setting
define an enumerator as N-uple, having the timesteps as first attribute


"""
