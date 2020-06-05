import logging
import numpy as np
import array
import pandas as pd
import uuid

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)


class MultiIndexedData(object):
    """
        This class allows to enumerate all the data combinations in a lazy style.
        Every combination is built upon its request by the client
    """
    _names=[] # Array containing the names associated to every column
    _data=[] # Array containing the data associated to every column
    _indexes=[] # Array containing the current index associated to every column
    _iteration_finished=False
    _iterations_counter=0
    _output_format = "simple"

    def __init__(self):
        logger.info("MultiIndexedData INIT")
        self._iterations_counter=1

    def __iter__(self):
        """
            Init the iterator (if used with the iter function)
        """
        logger.info("MultiIndexedData ITER")
        self._iterations_counter = 1
        self._iteration_finished = False
        for i, index in enumerate(self._indexes):
            logger.info(i)
            self._indexes[i] = 0
        logger.info(self._indexes)
        return self

    def __next__(self):
        """
            Get next data
        """
        #logger.info("MultiIndexedData NEXT")
        return self.get_next_data()

    def set_output_format(self, format="simple"):
        """
            Setup the output format
            format:
                "simple" => returns the array of data
                "full" => return the array of objects: { "name": "<name of column", "data": <the data>}
        """
        if format is not "simple" and format is not "full":
            raise Exception(f"The format {format} is not allowed!")
        self._output_format = format

    def add_data(self, name=None, data=None):
        """
            Used to add data to the structure, that can be an array-like or a single value
        """
        if isinstance(data, (list,array.array,range,np.ndarray)):
            self._data.append(data)
        else:
            self._data.append([data])
        self._indexes.append(0)

        if name is None:
            # Generating an UUID for the name
            name = str(uuid.uuid4())

        self._names.append(name)


    def get_next_data(self):
        """
            Gets the next index (not yet requested) and returns the associated data
        """
        next_index = self.get_next_index()
        next_data = []
        for col_count, index in enumerate(next_index):
            # print(f"col_count {col_count}, index: {index}")
            if self._output_format=="simple":
                next_data.append(self._data[col_count][index])
            elif self._output_format=="full":
                next_data.append({"name" : self._names[col_count], "data": self._data[col_count][index]})
            else:
                raise Exception(f"The format {self._output_format} is not allowed!")


        return next_data

    def get_current_iteration_count(self):
        """
            Returns the current iteration count
        """
        return self._iterations_counter

    def get_next_index(self):
        """
            Returns the first not used index
        """

        if self._iteration_finished:
            raise StopIteration

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
        self._iterations_counter = self._iterations_counter + 1

        return _new_index

    def get_current_index(self):
        """
            Returns the current index
        """
        return self._indexes.copy()




class ScenariosManager(object):
    """
        Multi Scenario Manager
    """
    _multi_scenario={
         "names":[],
    #     "values":[],
    #     "indexes":[]
    }
    _multi_id=None
    def __init__(self):
        logger.info("ScenariosManager INIT")
        self._multi_id = MultiIndexedData()

    def get_scenarios_iterator(self, format="simple"):
        """
            Returns an iterator to extraxt a scenario once at a time. Init the iterator to 1
            TIP: Calling this method before the event StopIteration causes a restart of the index
        """
        logger.info("ScenariosManager get_scenarios_iterator 1")
        self._multi_id.set_output_format(format)
        logger.info("ScenariosManager get_scenarios_iterator 2")
        return iter(self._multi_id)

    def get_next_index(self):
        """
            Returns the next index
        """
        return self._multi_id.get_next_index()

    def get_next_data(self):
        """
            Returns the next data, associating the indexed data with its names
        """
        out_data = []
        for i,item in enumerate(self._multi_id.get_next_data()):
            out_data.append({"name" : self._multi_scenario["names"][i], "value": item})
        return out_data

    def get_current_iteration_count(self):
        """
            Returns the current iteration count
        """
        return self._multi_id.get_current_iteration_count()


    def add_scenario(self, name, data):
        """
            Used to add a new scenario to the multi dimensional index
        """
        self._multi_scenario["names"].append(name)
        # self._multi_scenario["values"].append(data)
        # self._multi_scenario["indexes"].append(range(len(data)))

        self._multi_id.add_data(name=name, data=data)

    # def tuple_iterator(self):
    #     # returns the iterator of all the scenarios combinations
    #     print("tuple_iterator")
    #     iterables = np.array(self._multi_scenario["values"])
    #     print (iterables)
    #     #
    #     #pd.MultiIndex.from_product(iterables)
    #     for index in list(pd.MultiIndex.from_product(iterables)):
    #         yield index
    #
    # def indexes_iterator(self):
    #     # returns the iterator of all the scenarios combinations
    #     print("indexes_iterator")
    #     iterables = np.array(self._multi_scenario["indexes"])
    #     #
    #     #pd.MultiIndex.from_product(iterables)
    #     for index in list(pd.MultiIndex.from_product(iterables)):
    #         yield index



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
sm.add_scenario("r3.pippo",[9,8,7,6,5,4,3,2,1,20,21])
sm.add_scenario("r4.pluto",999)
sm.add_scenario(None,111)
sm.add_scenario("r4.minnie",[{"nome":12},{"cognome":12}])

# for it in sm.tuple_iterator():
#     print(it)
#
# for it in sm.indexes_iterator():
#     print(it)


# print (sm.get_next_index())
# while True:
#     my_data = sm.get_next_data()
#     print("{}: {}".format(sm.get_iteration_count(),my_data))


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
