import logging
from .multi_dimensional_data import MultiDimensionalData

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)


class ScenariosManager(object):
    """
        Multi Scenario Manager
    """
    def __init__(self, save_components_history=True):
        """
            Manager initialization
        """
        logger.info("ScenariosManager INIT")
        self._multi_scenario={
             "names":[],
        }
        self._multi_id = MultiDimensionalData(save_components_history = save_components_history)
        self._save_components_history = save_components_history

    #################################################

    def add_scenario(self, object_reference=None, object_type=None, object_name=None, property_name=None, property_data=None):
        """
            Used to add a new scenario to the multi dimensional index
        """
        self._multi_scenario["names"].append(object_name)

        self._multi_id.add_data(object_reference=object_reference, object_type=object_type, object_name=object_name, property_name=property_name, property_data=property_data)

    ###################################################

    def get_scenarios_iterator(self, format="simple"):
        """
            Returns an iterator to extraxt a scenario once at a time. Init the iterator to 1

            TIP: Calling this method before the event StopIteration causes ALWAYS a restart of the index

            USAGE of the iterator:
                for x in sm.get_scenarios_iterator("full"):
                    logger.info(x)
        """
        self._multi_id.set_output_format(format)
        return iter(self._multi_id)

    def get_scenario_ids_iterator(self):
        """
            Returns an iterator containing ONLY scenario_id!
        """
        return self.get_scenarios_iterator(format="id")


    ################################################################
    def get_full_scenarios_count(self):
        """
            Returns the full count of added scenarios
        """
        return self._multi_id.get_full_scenarios_count()


    def get_current_index(self):
        """
            Returns the current index of the multidimensional data manager without affecting the index
        """
        return self._multi_id.get_current_index()

    def get_current_scenario_id(self):
        """
            Returns the current index of the multidimensional data manager as a tuple without affecting the index
        """
        return self._multi_id.get_current_scenario_id()


    def get_current_data(self):
        """
            Returns the current data of the multidimensional data manager without affecting the index
        """
        return self._multi_id.get_current_data()

    def get_current_component_property_data(self, object_type=None, object_name=None, property_name=None):
        """
            Returns the current scenario data for the object which tuple is passed
        """
        return self._multi_id.get_current_object_property_data(object_type=object_type, object_name=object_name, property_name=property_name)

    #######################################

    def get_next_index(self):
        """
            Returns the next index of the multi dimensional data manager. The index is Incremented afterwards
        """
        return self._multi_id.get_next_index()

    def get_next_data(self):
        """
            Returns the next data, associating the indexed data with its names. The index is Incremented afterwards
        """
        out_data = []
        for i,item in enumerate(self._multi_id.get_next_data()):
            out_data.append({"name" : self._multi_scenario["names"][i], "value": item})
        return out_data

    ################################################

    def get_current_iteration_count(self):
        """
            Returns the current iteration count
        """
        return self._multi_id.get_current_iteration_count()
