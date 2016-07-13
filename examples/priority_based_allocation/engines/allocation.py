# -*- coding: utf-8 -*-

from pynsim import Engine

import pyomo.opt as opt
import pyomo.environ as pyomo


class PriorityBased(Engine):
    """Priority based water allocation engine. This alogorithm is based on the
    method described by Israel and Lund (1999).

    Israel, M. and Lund, J.: Priority Preserving Unit Penalties in Network Flow
    Modeling. Journal of Water Resources Planning and Management, 125,
    205-214, 1999.
    """
    name = "Priority based allocation engine using Coopr.pyomo and GLPK."
    target = None

    def _assign_id(self):
        n = 1
        while True:
            yield n
            n += 1

    def update(self):
        """Calculate optimal allocation for one time step.
        """
        # Create a concrete model
        model = pyomo.ConcreteModel()

        solver = opt.SolverFactory('glpk')

        # Determine node types
        node_types = dict()
        nodes = dict()
        node_names = dict()  # Needed to build connectivity matrix from links
        id_generator = self._assign_id()
        for node in self.target.nodes:
            n_id = id_generator.next()
            nodes[n_id] = node
            node_names[node.name] = n_id
            if node.type not in node_types.keys():
                node_types[node.type] = [n_id]
            else:
                node_types[node.type].append(n_id)

        # Determine link types
        link_types = dict()
        links = dict()
        connectivity = dict()
        for i in nodes.keys():
            for j in nodes.keys():
                connectivity[i, j] = 0
        for link in self.target.links:
            l_id = id_generator.next()
            links[l_id] = link
            startnode_id = node_names[link.start_node.name]
            endnode_id = node_names[link.end_node.name]
            connectivity[startnode_id, endnode_id] = l_id
            if link.type not in link_types.keys():
                link_types[link.type] = [l_id]
            else:
                link_types[link.type].append(l_id)

        # Define node and link type sets

        model.nodes = pyomo.Set(initialize=nodes.keys())

        model.InAndOut = pyomo.Set(initialize=node_types['InAndOut'],
                                   domain=pyomo.NonNegativeIntegers)
        model.Junction = pyomo.Set(initialize=node_types['Junction'],
                                   domain=pyomo.NonNegativeIntegers)
        model.Reservoir = pyomo.Set(initialize=node_types['Reservoir'],
                                    domain=pyomo.NonNegativeIntegers)
        model.Demand = pyomo.Set(initialize=node_types['Demand'],
                                 domain=pyomo.NonNegativeIntegers)

        model.links = pyomo.Set(initialize=links.keys())

        model.Channel = pyomo.Set(initialize=link_types['Channel'],
                                  domain=pyomo.NonNegativeIntegers)

        # Assign parameters
        # 'InAndOut' and 'Junction' nodes do not have any data

        #-- Reservoir
        init_stor = dict()
        max_stor = dict()
        min_stor = dict()
        carryover_penalty = dict()
        for res in node_types['Reservoir']:
            # Assign storage of the last simulation, if available. Use
            # init_stor otherwise
            if len(nodes[res]._history['S']) == 0:
                init_stor[res] = nodes[res].init_stor
            else:
                init_stor[res] = nodes[res]._history['S'][-1]
            max_stor[res] = nodes[res].max_stor
            min_stor[res] = nodes[res].min_stor
            carryover_penalty[res] = nodes[res].carryover_penalty

        model.Res_init_stor = pyomo.Param(model.Reservoir, within=pyomo.Reals,
                                          initialize=init_stor)
        model.Res_max_stor = pyomo.Param(model.Reservoir, within=pyomo.Reals,
                                         initialize=max_stor)
        model.Res_min_stor = pyomo.Param(model.Reservoir, within=pyomo.Reals,
                                         initialize=min_stor)
        model.Res_carryover_penalty = pyomo.Param(model.Reservoir,
                                                  within=pyomo.Reals,
                                                  initialize=carryover_penalty)

        #-- Demand
        cons_coeff = dict()
        for dem in node_types['Demand']:
            cons_coeff[dem] = nodes[dem].consumption_coeff
        model.Dem_consumption_coeff = pyomo.Param(model.Demand,
                                                  within=pyomo.Reals,
                                                  initialize=cons_coeff)

        #-- Channel
        cost = dict()
        flowmult = dict()
        max_flow = dict()
        min_flow = dict()
        for cha in link_types['Channel']:
            cost[cha] = links[cha].cost
            flowmult[cha] = links[cha].flowmult
            max_flow[cha] = links[cha].max_flow
            min_flow[cha] = links[cha].min_flow
        model.Cha_cost = pyomo.Param(model.Channel, within=pyomo.Reals,
                                     initialize=cost)
        model.Cha_flowmult = pyomo.Param(model.Channel, within=pyomo.Reals,
                                         initialize=flowmult)
        model.Cha_max_flow = pyomo.Param(model.Channel, within=pyomo.Reals,
                                         initialize=max_flow)
        model.Cha_min_flow = pyomo.Param(model.Channel, within=pyomo.Reals,
                                         initialize=min_flow)

        # Connectivity matrix
        model.connectivity = pyomo.Param(model.nodes, model.nodes,
                                         within=pyomo.NonNegativeIntegers,
                                         initialize=connectivity)

        # Assign variables
        #-- InAndOut
        model.InA_Q = pyomo.Var(model.InAndOut, domain=pyomo.Reals)

        #-- Reservoir - no negative storage allowed
        model.Res_S = pyomo.Var(model.Reservoir, domain=pyomo.NonNegativeReals)

        #-- Demand - no negative delivery allowed
        model.Dem_delivery = pyomo.Var(model.Demand,
                                       domain=pyomo.NonNegativeReals)

        #-- Channel
        model.Cha_Q = pyomo.Var(model.Channel, domain=pyomo.Reals)

        # Set constraints
        def storage_limits(model, res):
            "Set minimum and maximum storage on reservoirs."
            return (model.Res_min_stor[res], model.Res_S[res],
                    model.Res_max_stor[res])

        model.storage_limits = pyomo.Constraint(model.Reservoir,
                                                rule=storage_limits)

        def flow_limits(model, chan):
            "Set minimum and maximum flow on channels."
            return (model.Cha_min_flow[chan], model.Cha_Q[chan],
                    model.Cha_max_flow[chan])

        model.flow_limits = pyomo.Constraint(model.Channel, rule=flow_limits)

        def mass_balance(model, node):
            "Make sure the mass balance is closed in all nodes."
            tot_outflow = 0  # Flow from node
            tot_inflow = 0  # Flow to node
            for i in model.nodes:
                out_link = model.connectivity[node, i]
                if out_link != 0:
                    tot_outflow += model.Cha_Q[out_link]
                in_link = model.connectivity[i, node]
                if in_link != 0:
                    tot_inflow += model.Cha_Q[in_link] \
                        * model.Cha_flowmult[in_link]

            if node in model.InAndOut:
                return model.InA_Q[node] == tot_outflow - tot_inflow
            elif node in model.Reservoir:
                return model.Res_S[node] == model.Res_init_stor[node] \
                    + tot_inflow - tot_outflow
            elif node in model.Demand:
                return model.Dem_delivery[node] == tot_inflow \
                    * model.Dem_consumption_coeff[node]  # No return flow
            else:  # Junction nodes
                return tot_inflow == tot_outflow

        model.mass_balance = pyomo.Constraint(model.nodes, rule=mass_balance)

        # Define objective function

        def objective(model):
            "Objective function: sum of cost_i * flow_i"
            flow_cost = sum(model.Cha_Q[i] * model.Cha_cost[i]
                            for i in model.links)
            carryover_cost = sum(model.Res_S[i] *
                                 model.Res_carryover_penalty[i]
                                 for i in model.Reservoir)
            return flow_cost + carryover_cost

        model.objective = pyomo.Objective(rule=objective, sense=pyomo.minimize)

        # Run optimisation
        #model_instance = model.create_instance()
        #result = solver.solve(model_instance)
        #model_instance.load(result)
        result = solver.solve(model)
        model.solutions.load_from(result)

        # Extract results
        #-- Assign node variables
        self.target.nodes = []

        for node_id in node_types['Reservoir']:
            node = nodes[node_id]
            node.S = model.Res_S[node_id].value
            self.target.nodes.append(node)
        for node_id in node_types['Demand']:
            node = nodes[node_id]
            node.delivery = model.Dem_delivery[node_id].value
            self.target.nodes.append(node)
        for node_id in node_types['InAndOut']:
            node = nodes[node_id]
            node.Q = model.InA_Q[node_id].value
            self.target.nodes.append(node)
        for node_id in node_types['Junction']:
            # No results here, but the node is needed in the following
            # timesteps
            self.target.nodes.append(nodes[node_id])

        #-- Assign link variables
        self.target.links = []

        for link_id, link in links.iteritems():
            link.Q = model.Cha_Q[link_id].value
            self.target.links.append(link)

        #-- Assign objective
        self.target.cost = sum(link.cost * link.Q for link in self.target.links)
