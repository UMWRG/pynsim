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

from pynsim import Engine

from pyomo.environ import *

from PyModel import PyomModel

class PyomoAllocation(Engine):

    name   = """A pyomo-based engine which allocates water throughout a whole
    network in a single time-step."""
    target = None
    storage={}

    def update(self):
        """
            Calling Pyomo model
        """
        pp =PyomModel(self.target)
        instance =pp.run()

        print("========= Timestep: %s ============="%self.target.current_timestep)
        allocation =   "==========  Allocation       ============="
        storage="==========  storage    =============="

        delivery=" ==========  delivery ============="

        for var in instance.active_components(Var):
            if(var=="S"):
                s_var = getattr(instance, var)
                for vv in s_var:
                    name= ''.join(map(str,vv))
                    print(name, s_var[vv].value)
                    self.storage[name]=(s_var[vv].value)
                    storage+='\n'+ name+": "+ str(s_var[vv].value)
            elif var=="delivery":
                d_var = getattr(instance, var)
                for vv in d_var:
                    name= ''.join(map(str,vv))
                    self.storage[name]=(d_var[vv].value)
                    delivery+='\n'+ name+": "+ str(d_var[vv].value)
            elif var=="X":
                    x_var = getattr(instance, var)
                    for xx in x_var:
                        name= "(" + ', '.join(map(str,xx)) + ")"
                        #name=xx[1]
                        allocation+='\n'+name+": "+str(x_var[xx].value)

        print(allocation)
        print(storage)
        print(delivery)
        self.target.set_initial_storage(self.storage)

