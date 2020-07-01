import types
import array

import numpy as np


class PropertyObjectData(object):
    """
        This class represents the single object identified by the tuple
            (object-type, object-name, property-name)
    """
    def __init__(self, **kwargs):
        self._structure = types.SimpleNamespace()

        self._structure.current_index = None

        self._structure.object_type = None
        self._structure.object_name = None
        self._structure.object_reference = None
        self._structure.property_name = None
        self._structure.property_data = []

        self.set_data(**kwargs)

    def set_data(
                    self,
                    object_reference=None,
                    object_type=None,
                    object_name=None,
                    property_name=None,
                    property_data=None
                ):
        """
            Used to add data to the structure, that can be an array-like or a single value.
            The set_data replaces the current contained data
        """
        if object_type is None:
            raise Exception("The data type has to be associated with a valid object type!")
        self._structure.object_type = object_type

        self._structure.property_name = property_name
        if isinstance(property_data, (list,array.array,range,np.ndarray)):
            self._structure.property_data = property_data
        else:
            self._structure.property_data = [property_data]

        if object_name is None:
            raise Exception("The data name has to be associated with a valid object name!")

        self._structure.object_name = object_name

        # We need an unique reference to every column
        self._structure.object_reference = object_reference

        # The current index is 0
        self._structure.current_index = 0

    def get_data(self, format = "simple", index=None):
        """
            Returns the data related to the index provided
        """
        if index is None:
            raise Exception("It is necessary specify the index")
        if format=="simple":
            return self._structure.property_data[index]
        elif format=="full" or format=="tree":
            return {
                "object_type" : self._structure.object_type,
                "object_name" : self._structure.object_name,
                "object_reference" : self._structure.object_reference,
                "property_name": self._structure.property_name,
                "property_data": self._structure.property_data[index],
                "current_index": self._structure.current_index
            }
        elif format=="id":
            """
                Returns just the scenario id
            """
            return self._structure.current_index
        else:
            raise Exception(f"The format {format} is not allowed!")

    def get_current_indexed_data(self, format = "simple"):
        """
            Returns the data related to the current index
        """
        return self.get_data(index=self._structure.current_index)

    def get_current_index(self):
        """
            Returns the current index
        """
        return self._structure.current_index

    def set_current_index(self, index=None):
        """
            Sets the current index
        """
        if index is None:
            raise Exception("It is necessary specify the index")
        self._structure.current_index = index

    def data_length(self):
        """
            Returns the data length
        """
        return len(self._structure.property_data)
