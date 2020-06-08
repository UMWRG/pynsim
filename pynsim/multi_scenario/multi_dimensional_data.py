"""
    This class is a generic manager for multidimensional data
"""

import logging
import numpy as np
import array
# import pandas as pd
import uuid

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)


class MultiDimensionalData(object):
    """
        This class allows to enumerate all the data combinations in a lazy style.
        Every combination is built upon its request by the client
    """
    _references=[] # Array containing the referneces to the objects associated to every column
    _names=[] # Array containing the names associated to every column
    _data=[] # Array containing the data associated to every column
    _indexes=[] # Array containing the current index associated to every column
    _iteration_finished=False
    _iterations_counter=0
    _output_format = "simple"

    def __init__(self):
        logger.info("MultiDimensionalData INIT")
        self._iterations_counter=1

    def __iter__(self):
        """
            Init the iterator (if used with the iter function)
        """
        logger.info("MultiDimensionalData ITER")
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
        #logger.info("MultiDimensionalData NEXT")
        return self.get_next_data()

    ###################################################

    def set_output_format(self, format="simple"):
        """
            Setup the output format
            format:
                "simple" => returns the array of data
                "full" => return the array of objects: { "name": "<name of column>", "reference": "<reference of column>", "data": <the data>}
        """
        if format is not "simple" and format is not "full":
            raise Exception(f"The format {format} is not allowed!")
        self._output_format = format

    def add_data(self, name=None, reference=None, data=None):
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

        # We need an unique reference to every column
        self._references.append(reference)


    def get_next_data(self):
        """
            Gets the next index (not yet requested) and returns the associated data
        """
        next_data = self.get_current_data()
        self._increment_index()

        # next_index = self.get_next_index()
        # next_data = []
        # for col_count, index in enumerate(next_index):
        #     # print(f"col_count {col_count}, index: {index}")
        #     if self._output_format=="simple":
        #         next_data.append(self._data[col_count][index])
        #     elif self._output_format=="full":
        #         next_data.append({
        #             "name" : self._names[col_count],
        #             "reference" : self._references[col_count],
        #             "data": self._data[col_count][index]
        #         })
        #     else:
        #         raise Exception(f"The format {self._output_format} is not allowed!")
        #

        return next_data

    #######################################################################################

    def get_current_data(self, increment_index=False):
        """
            Gets the data referred by the current index.
                After getting the data,  based upon the 'increment_index' value:
                False => The index is not modified at all
                True  => The index is incremented
        """
        data_index = self.get_current_index()
        next_data = []
        for col_count, index in enumerate(data_index):
            # print(f"col_count {col_count}, index: {index}")
            if self._output_format=="simple":
                next_data.append(self._data[col_count][index])
            elif self._output_format=="full":
                next_data.append({
                    "name" : self._names[col_count],
                    "reference" : self._references[col_count],
                    "data": self._data[col_count][index]
                })
            else:
                raise Exception(f"The format {self._output_format} is not allowed!")


        if increment_index is True:
            self._increment_index()

        return next_data


    def _increment_index(self):
        """
            Increments the index, if possible, raise StopIteration otherwise
        """
        if self._iteration_finished:
            raise StopIteration

        flag_update_index_done = False

        for main_list_index, datum  in reversed(list(enumerate(self._data))):
            datum_length=len(datum)
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

    #################################################

    # def get_next_index(self):
    #     """
    #         Returns the first not used index
    #     """
    #
    #     if self._iteration_finished:
    #         raise StopIteration
    #
    #     flag_update_index_done = False
    #
    #     _new_index=self._indexes.copy()
    #
    #     for main_list_index, datum  in reversed(list(enumerate(self._data))):
    #         # print(f"datum {datum}")
    #         # print(f"main_list_index {main_list_index}")
    #         datum_length=len(datum)
    #         current_datum_index=self._indexes[main_list_index]
    #
    #         # print(f"datum_length: {datum_length} current_datum_index: {current_datum_index}")
    #         if flag_update_index_done is False:
    #             # I have to check the current index
    #             if current_datum_index < ( datum_length - 1 ):
    #                 # Increment the index for that column
    #                 self._indexes[main_list_index] = self._indexes[main_list_index] + 1
    #                 flag_update_index_done = True
    #                 break
    #             else:
    #                 # Column index overflow
    #                 self._indexes[main_list_index] = 0
    #
    #     self._iteration_finished = not flag_update_index_done
    #     self._iterations_counter = self._iterations_counter + 1
    #
    #     return _new_index
