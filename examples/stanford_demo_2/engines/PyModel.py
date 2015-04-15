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

from pyomo.environ import *

class PyomModel:
    # Declaring the model

     def __init__(self, network):
        '''
         set up the model data
         get the the required data from network and saved in list and dictionary data structures
         then will be used to initialized the Pyomo model
         the parameters and variables have meaninful name
        '''

        self.nodes_names=[]
        self.demand_nodes=[]
        self.storage_nodes=[]
        self.nonstorage_nodes=[]
        self.node_initial_storage={}
        self.links_comp={}
        self.flow_multiplier={}
        self.min_storage={}
        self.max_storage={}
        self.inflow={}
        self.consumption_coefficient={}
        self.upper_flow={}
        self.lower_flow={}
        self.flow_multiplier={}
        self.cost={}

        #itrate the network nodes to extract nodes data

        for node in  network.nodes:
            self.nodes_names.append(node.name)
            self.inflow[(node.name)]=node.inflow
            if node.type == 'agricultural' or node.type == 'urban':
                print(node.demand)
                self.demand_nodes.append(node.name)
                self.consumption_coefficient[(node.name)]=node.consumption_coefficient
            else:
                self.consumption_coefficient[(node.name)]=0

            if node.type == 'surface reservoir':
                self.storage_nodes.append(node.name)
                self.node_initial_storage[(node.name)]=node.initial_storage
                self.min_storage[(node.name)]=node.min_storage
                self.max_storage[(node.name)]=node.max_storage


            if node.type=='junction' or node.type== 'agricultural' or node.type=='urban':
                self.nonstorage_nodes.append(node.name)

        #itrate the network links to extract the required data
        #the link is defined by two nodes i.e. start_node, and end_node

        for link in network.links:
            self.links_comp[(link.start_node.name, link.end_node.name)]=link
            self.flow_multiplier[(link.start_node.name, link.end_node.name)]=link.flow_multiplier
            self.upper_flow[(link.start_node.name, link.end_node.name)]=link.upper_flow
            self.lower_flow[(link.start_node.name, link.end_node.name)]=link.lower_flow
            self.cost[(link.start_node.name, link.end_node.name)]=link.cost

     def run(self):
         # Create the model
        model = AbstractModel()
        # Declaring model indexes using sets
        model.nodes = Set(initialize=self.nodes_names)
        model.links = Set(within=model.nodes*model.nodes, initialize=self.links_comp.keys())
        model.demand_nodes = Set(initialize=self.demand_nodes)
        model.nonstorage_nodes = Set(initialize=self.nonstorage_nodes)
        model.storage_nodes = Set(initialize=self.storage_nodes)
        model.initial_storage = Param(model.storage_nodes, mutable=True, initialize=self.node_initial_storage)

        # Declaring model parameters
        model.inflow = Param(model.nodes, initialize=self.inflow)

        model.consumption_coefficient = Param(model.nodes, initialize=self.consumption_coefficient)
        model.cost = Param(model.links, initialize=self.cost)
        model.flow_multiplier = Param(model.links, initialize=self.flow_multiplier)
        model.flow_lower_bound = Param(model.links, initialize= self.lower_flow)
        model.flow_upper_bound = Param(model.links, initialize=self.upper_flow)
        model.storage_lower_bound = Param(model.storage_nodes, initialize=self.min_storage)
        model.storage_upper_bound = Param(model.storage_nodes, initialize=self.max_storage)
        #model.demand = Param(model.demand_nodes, model.time_step)

        ##======================================== Declaring Variables (X and S)

        # Defining the flow lower and upper bound
        def flow_capacity_constraint(model, node, node2):
            return (model.flow_lower_bound[node, node2], model.flow_upper_bound[node, node2])

        # Defining the storage lower and upper bound
        def storage_capacity_constraint(model, storage_nodes):
            return (model.storage_lower_bound[storage_nodes], model.storage_upper_bound[storage_nodes])

        # Declaring decision variable X
        model.X = Var(model.links, domain=NonNegativeReals, bounds=flow_capacity_constraint)

        # Declaring state variable S
        model.S = Var(model.storage_nodes, domain=NonNegativeReals, bounds=storage_capacity_constraint)

        #Declaring delivery
        model.delivery=Var(model.demand_nodes, domain=NonNegativeReals)

        ##======================================== Declaring the objective function (Z)
        def objective_function(model):
            return summation(model.cost, model.X)

        model.Z = Objective(rule=objective_function, sense=minimize)

        ##======================================== Declaring constraints

        # Mass balance for non-storage nodes:4
        def set_delivery(instance):
            for var in instance.active_components(Var):
                    if(var=="delivery"):
                        s_var = getattr(instance, var)
                        for vv in s_var:
                            #s_var[vv]=-2
                            sum=0
                            for var_2 in instance.active_components(Var):
                                if(var_2=="X"):
                                    s_var_2 = getattr(instance, var_2)
                                    for vv2 in s_var_2:
                                        if(vv in vv2):
                                            sum=sum+s_var_2[vv2].value
                            s_var[vv]=sum

        def mass_balance(model, nonstorage_nodes):

            # inflow
            term1 = model.inflow[nonstorage_nodes]
            term2 = sum([model.X[node_in, nonstorage_nodes]*model.flow_multiplier[node_in, nonstorage_nodes]
                          for node_in in model.nodes if (node_in, nonstorage_nodes) in model.links])

            # outflow
            term3 = model.consumption_coefficient[nonstorage_nodes] \
                * sum([model.X[node_in, nonstorage_nodes]*model.flow_multiplier[node_in, nonstorage_nodes]
                       for node_in in model.nodes if (node_in, nonstorage_nodes) in model.links])
            term4 = sum([model.X[nonstorage_nodes, node_out]
                          for node_out in model.nodes if (nonstorage_nodes, node_out) in model.links])

            return (term1 + term2) - (term3 + term4) == 0

        model.mass_balance_const = Constraint(model.nonstorage_nodes, rule=mass_balance)

        # Mass balance for storage nodes:
        def storage_mass_balance(model, storage_nodes):
            # inflow
            term1 = model.inflow[storage_nodes]
            term2 = sum([model.X[node_in, storage_nodes]*model.flow_multiplier[node_in, storage_nodes]
                          for node_in in model.nodes if (node_in, storage_nodes) in model.links])

            # outflow
            term3 = sum([model.X[storage_nodes, node_out]
                          for node_out in model.nodes if (storage_nodes, node_out) in model.links])

            # storage
            term4 = model.initial_storage[storage_nodes]

            term5 = model.S[storage_nodes]

            # inflow - outflow = 0:
            return (term1 + term2 + term4) - (term3 + term5) == 0

        model.storage_mass_balance_const = Constraint(model.storage_nodes, rule=storage_mass_balance)
        ##======================== running the model in a loop for each time step

        # set the solver
        opt = SolverFactory("glpk")
        #create the model instance
        instance=model.create()
        #solve the model
        result=opt.solve(instance)
        instance.load(result)
        set_delivery(instance)
        return instance

