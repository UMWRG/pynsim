"""
    This class is a generic manager for multidimensional data
"""

import logging
import numpy as np
import array
import uuid

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

from .property_object_data import PropertyObjectData

class MultiDimensionalData(object):
    """
        This class allows to enumerate all the data combinations in a lazy style.
        Every combination is built upon its request by the client
    """

    def __init__(self, save_components_history = True):
        # logger.info("MultiDimensionalData INIT")

        self._objects_map = {} # Map of the indexes used for all the oject indexed ty the tuple (object type, object name, property name)

        self._objects_list = []
        self._indexes=[] # Array containing the current index associated to every column

        self._iteration_finished=False
        self._iterations_counter=0
        self._output_format = "simple"

        self._iterations_counter=1

        self._save_components_history = save_components_history

    def __iter__(self):
        """
            Init the iterator (if used with the iter function)
        """
        # logger.info("MultiDimensionalData ITER")
        self._iterations_counter = 1
        self._iteration_finished = False
        for i, index in enumerate(self._indexes):
            # logger.info(i)
            self._indexes[i] = 0
        # logger.info(self._indexes)
        return self

    def __next__(self):
        """
            Get next data
        """
        return self.get_next_data()

    ###################################################

    def set_output_format(self, format="simple"):
        """
            Setup the output format
            format:
                "simple" => returns the array of data
                "full" => return the array of objects: { "name": "<name of column>", "reference": "<reference of column>", "data": <the data>}
                "tree" => returns a tree organized by object_type.object_name.property_name
        """
        if format is not "simple" and format is not "full" and format is not "tree":
            raise Exception(f"The format {format} is not allowed!")
        self._output_format = format


    def get_tuple_index(self, object_type=None, object_name=None, property_name=None):
        """
            Returns the tuple:
                ( object_type, object_name, property_name )
        """
        if object_type is None:
            raise Exception("The Object Type cannot be None")

        if object_name is None:
            raise Exception("The Object Name cannot be None")

        if property_name is None:
            raise Exception("The Property Name cannot be None")

        return f"{object_type.strip().lower()},{object_name.strip().lower()},{property_name.strip().lower()}"

    def add_data(self, object_reference=None, object_type=None, object_name=None, property_name=None, property_data=None):
        """
            Add data related to the tuple
                ( object_type, object_name, property_name )
        """
        unique_id = self.get_tuple_index(object_type, object_name, property_name)
        if unique_id in self._objects_map:
            raise Exception(f"The tuple ({unique_id}) has been already defined!")

        new_object = PropertyObjectData(object_reference=object_reference, object_type=object_type, object_name=object_name, property_name=property_name, property_data=property_data)

        self._objects_map[unique_id] = len(self._objects_list)
        self._indexes.append(0)
        self._objects_list.append(new_object)

    def get_next_data(self):
        """
            Gets the current indexed data
            The index is incremented
        """
        data = self.get_current_data(increment_index=True)

        return data

    #######################################################################################
    def get_current_object_property_data(self, object_type=None, object_name=None, property_name=None):
        """
            Returns the current scenario data for the provided object/property
        """
        unique_id = self.get_tuple_index(object_type, object_name, property_name)
        if unique_id not in self._objects_map:
            raise Exception(f"The tuple ({unique_id}) has not been yet defined!")


        object_property_all_data_mgr = self._objects_list[ self._objects_map[unique_id] ]
        object_scenario_index = self._indexes[ self._objects_map[unique_id] ]
        return object_property_all_data_mgr.get_data(index=object_scenario_index)

    def get_current_data(self, increment_index=False):
        """
            Gets the data referred by the current index.
                After getting the data,  based upon the 'increment_index' value:
                False => The index is not modified at all
                True  => The index is incremented
        """
        data_index = self.get_current_index()

        if self._output_format == "tree":
            current_data = {}
        else:
            current_data = []

        for col_count, index in enumerate(data_index):

            item_data = self._objects_list[col_count].get_data(index=index, format=self._output_format)
            if self._output_format == "tree":
                """
                    In this case the full data are returned as a tree
                """
                if not item_data["object_type"] in current_data:
                    current_data[item_data["object_type"]] = {}
                if not item_data["object_name"] in current_data[item_data["object_type"]]:
                    current_data[item_data["object_type"]][item_data["object_name"]] = {
                        "reference": item_data["object_reference"],
                        "properties": {}
                    }
                if not item_data["property_name"] in current_data[item_data["object_type"]][item_data["object_name"]]["properties"]:
                    current_data[item_data["object_type"]][item_data["object_name"]]["properties"][item_data["property_name"]] = {
                        "data"      : item_data["property_data"],
                        # "reference" : item_data["object_reference"],
                        "current_index" : item_data["current_index"]
                    }
                else:
                    raise Exception("Error")
            else:
                current_data.append(item_data)

        index_tuple = self.get_current_scenario_id()

        if increment_index is True:
            self._increment_index()

        return {"data": current_data, "index": data_index, "tuple": index_tuple}


    def _increment_index(self):
        """
            Increments the index, if possible, raise StopIteration otherwise
        """
        if self._iteration_finished:
            raise StopIteration

        flag_update_index_done = False

        for main_list_index, obj  in reversed(list(enumerate(self._objects_list))):

            datum_length=obj.data_length()
            current_datum_index=self._indexes[main_list_index]

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

        self._iteration_finished = not flag_update_index_done # In case that it has not been possible incrementing the index => we finished the possible indexes
        self._iterations_counter = self._iterations_counter + 1

        for index, index_value in enumerate(self._indexes):
            # The index inside every object is updated
            self._objects_list[index].set_current_index(index_value)

    def get_current_scenario_id(self):
        """
            Returns the current index as a tuple in order to be used as index of a dict, if available, StopIteration otherwise
        """
        if self._iteration_finished:
            raise StopIteration
        return ','.join([str(x) for x in self._indexes])

    def get_current_index(self):
        """
            Returns the current index, if available, StopIteration otherwise
        """
        if self._iteration_finished:
            raise StopIteration
        return self._indexes.copy()

    def get_current_iteration_count(self):
        """
            Returns the current iteration count
        """
        return self._iterations_counter
