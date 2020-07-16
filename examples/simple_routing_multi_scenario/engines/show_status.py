# -*- coding: utf-8 -*

from pynsim import Engine

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)s:%(message)s"
)
logger = logging.getLogger(__name__)

class ShowStatus(Engine):
    """
        This engine just shows the status of the iteration
    """

    name = "Show status"
    target = None

    def run(self):
        """
            execute the show
        """
        # logger.warning("This is the current scenario index: {}".format(self.simulator.get_current_scenario_index()))
        logger.warning("This is the current scenario serial index: {}".format(self.simulator.get_current_scenario_serial_index()))
        if self.simulator.loop_priority == "scenario":
            logger.warning("This is the timestep {} of the scenario {}".format(self.simulator.current_timestep, self.simulator.current_scenario_id))
        elif self.simulator.loop_priority == "timestep":
            logger.warning("This is the scenario {} of the timestep {}".format( self.simulator.current_scenario_id, self.simulator.current_timestep))
