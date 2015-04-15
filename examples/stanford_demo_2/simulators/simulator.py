#    (c) Copyright 2014, University of Manchester
#
#    This file is part of PyNSim.
#
#    PyNSim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNSim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNSim.  If not, see <http://www.gnu.org/licenses/>.

class Simulator(object):

    network = None 
    timesteps = []
    models = []

    def __repr__(self):
        my_models=",".join([m.name for m in self.models])
        return "Simulator(models=[%s])"%(my_models)

    def start(self):
        for timestep in self.timesteps:
            for model in self.models():
                model.run(timestep)

    def pause(self):
        pass

    def stop(self):
        pass

    def add_model(self, model, depends_on=[]):

        for dependant in depends_on:
            if dependant not in self.models:
                raise Exception("Model %s depends on %s but it is not in the"
                                " list of models.")

        self.model.append(model)

    def set_timesteps(self, timesteps, start_time=None, frequency=None, periods=None):
        if timesteps:
            self.timesteps = timesteps
        else:
            raise Exception("Not implemented yet.")
