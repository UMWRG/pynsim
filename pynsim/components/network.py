from .container import Container, logging, logger

class Network(Container):
    """
        A container for nodes, links and institutions.
    """
    base_type = 'network'

    def __init__(self, name, **kwargs):
        super(Network, self).__init__(name, **kwargs)

        #Track the timing of the setup functions for each node,link and institution
        self.timing = {'nodes':{}, 'links':{}, 'institutions':{}, 'unknown':{}}

        self.current_timestep = None
        self.current_timestep_idx = None


    def export_history(self, export_type='pickle',
                      complete=True,
                      reset_history=False,
                      include_all_components=False,
                      validate_before_export=False,
                      target_dir=None):
        """
            Export the history of the network and all sub-components into a pickled
            file, timestamped and in a './history' folder.

            args:
                complete Boolean: When set to False, only export the properties set in the '_result_properties' attribute
                export_type string:  The format of the exported file ('json' or 'pickle). Json is more human readable and has greater cross-compatibility, but pickles allow saving of more complex data structures (objects). Default is JSON.
                reset_history Boolean: Empty the history dict for each component after export, useful when the same network is being used for multiple simulations.
                include_all_components Boolean: If there are components in the network which are not nodes, links or institutions, use this flag to export their history
                target_dir string: A path to the location of the history export (THis will create a 'history' folder within the target directory)
        """

        if complete is True:
            logging.warning("Exporting the complete history can result in large files."+
                            " Please consider setting 'complete=False' and specifying the"+
                            "properties you wish to export in your agents class like so: _result_properties = [propa, prob, ...]")


        history = Map({'nodes' : Map(), 'links' : Map(), 'institutions' : Map(), 'network': Map(), 'other': Map()})

        if complete is True:
            Map(self._history)
        else:
            truncated_history = {}
            for param_name in self._result_properties:
                truncated_history[param_name] = self._history[param_name]
            history['network'][self.name] = Map(truncated_history)

        for c in self.components:

            if validate_before_export is True:
                if not c.validate_history():
                    continue

            if c.base_type == 'node':
                if complete is True:
                    history['nodes'][c.name] = Map(c._history)
                else:
                    truncated_history = {}
                    for param_name in c._result_properties:
                        truncated_history[param_name] = c._history[param_name]
                    history['nodes'][c.name] = Map(truncated_history)
            elif c.base_type == 'link':
                if complete is True:
                    history['links'][c.name] = Map(c._history)
                else:
                    truncated_history = {}
                    for param_name in c._result_properties:
                        truncated_history[param_name] = c._history[param_name]
            elif c.base_type == 'institution':
                if complete is True:
                    history['institutions'][c.name] = Map(c._history)
                else:
                    truncated_history = {}
                    for param_name in c._result_properties:
                        truncated_history[param_name] = c._history[param_name]

            else:
                if include_all_components is True:
                    if complete is True:
                        history['other'][c.name] = Map(c._history)
                else:
                    truncated_history = {}
                    for param_name in c._result_properties:
                        truncated_history[param_name] = c._history[param_name]

        if target_dir is None:
            target_dir  = os.path.dirname(os.path.realpath(sys.argv[0]))

        hist_dir    = os.path.join(target_dir, 'history')

        if not os.path.exists(hist_dir):
            os.mkdir(hist_dir)

        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        export_path = None
        try:
            with open(os.path.join(hist_dir, 'sim_'+now+'.json'), 'w') as json_file:
                json_file.write(json.dumps(history, indent=4))
                export_path = os.path.join(hist_dir, 'sim_'+now+'.json')
        except TypeError:
            os.remove(os.path.join(hist_dir, 'sim_'+now+'.json'))

            logging.warning('Unable to dump to JSON, trying a pickle')
            with open(os.path.join(hist_dir, 'sim_'+now+'.pickle'), 'w') as f:
                pickle.dump(history, f)
                export_path = os.path.join(hist_dir, 'sim_'+now+'.pickle')
        except Exception:
            logging.critical("Unable to export history. "
                            "Is one of your component properties too complex, like a method?")

        if reset_history == True:
            self.reset_history()
            for c in self.components:
                c.reset_history()


        logging.info('History Dumped to %s' % export_path)

    def set_timestep(self, timestamp, timestep_idx):
        """
            Set the current timestep in the simulation as an attribute
            on the network.
        """
        self.current_timestep = timestamp
        self.current_timestep_idx = timestep_idx

    def post_process(self):
        """
            Once all the appropriate values have been set, ensure that the
            values are saved for subsequent use.
        """

        super(Network, self).post_process()
        for c in self.components:
            c.post_process()

    def setup_components(self, timestamp, record_time=False):
        """
            Call the setup function of each of the nodes in the network
            in turn.

            :returns The time it took to call the function (in seconds)
        """

        time_dict = {'nodes':0, 'links':0, 'institutions':0, 'unknown':0}

        for c in self.components:
            try:

                if record_time is True:
                    individual_time = time.time()

                c.setup(timestamp)

                if record_time is True:
                    #Compile the timing dictionary
                    setup_time = time.time()-individual_time
                    if c.base_type == 'node':
                        self.timing['nodes'][c.name] += setup_time
                        time_dict['nodes'] += setup_time
                    elif c.base_type == 'link':
                        self.timing['links'][c.name] += setup_time
                        time_dict['links'] += setup_time
                    elif c.base_type == 'institution':
                        self.timing['institutions'][c.name] += setup_time
                        time_dict['institutions'] += setup_time
                    elif c.base_type == 'component':
                        self.timing['unknown'][c.name] += setup_time
                        time_dict['unknown'] += setup_time
            except:
                logging.critical("An error occurred setting up node %s"
                                 " (timestamp=%s)", c.name, timestamp)
                raise

        return time_dict

    @property
    def connectivity(self):
        """
            Return a dictionary representing the connectivity matrix of the
            network.
        """
        connectivity = dict()

        # Connectivity
        node_names = dict()

        for i, node in enumerate(self.nodes):
            node_names[node.name] = i

        for i, node_from in enumerate(self.nodes):
            for j, node_to in enumerate(self.nodes):
                connectivity[i, j] = 0

        for i, link in enumerate(self.links):
            startnode_id = node_names[link.start_node.name]
            endnode_id = node_names[link.end_node.name]
            connectivity[startnode_id, endnode_id] = 1

        return connectivity

    def draw(self, block=True):
        """
            Draw the pynsim network as a matplotlib plot.
        """
        try:
            import matplotlib.pyplot as plt
            import networkx as nx

            g = nx.Graph()
            #Nodes
            pos = {}
            labels = {}
            for n in self.nodes:
                g.add_node(n)
                pos[n] = (n.x, n.y)
                labels[n] = n.name
            colours = [n.colour for n in g.nodes()]
            nx.draw_networkx_nodes(g, pos, width=8, alpha=0.5,
                                   node_color=colours)
            nx.draw_networkx_labels(g, pos, labels, font_size=10)
            #links
            for l in self.links:
                g.add_edge(l.start_node, l.end_node, name=l.name,
                           colour=l.colour)
            colours = [g[a][b]['colour'] for a, b in g.edges()]

            nx.draw_networkx_edges(g, pos, width=2, alpha=0.5,
                                   edge_color=colours)
            mng = plt.get_current_fig_manager()
            mng.resize(1000, 700)
            plt.show(block=block)

        except ImportError:
            logging.critical("Cannot draw network. Please ensure matplotlib "
                             "and networkx are installed.")


    def plot_timing(self, component):
        """
         Plot the total time taken to run the setup function of the
         components in the network.

         :param one of the following: 'nodes', 'links', 'institutions'
        """
        #Import seaborn to prettify the graphs if possible
        try:
            import seaborn
        except:
            pass

        try:
            import matplotlib.pyplot as plt

            width = 0.35

            s = self.timing[component].values()
            labels = self.timing[component].keys()
            t = range(len(s)) #Make a list [0, 1, 2...len(s)]
            pos = []
            for x in t:
                pos.append(x+0.15)

            fig, ax = plt.subplots()

            rects1 = ax.bar(t, s, width, color='r')
            ax.set_xticks(pos)
            ax.set_xticklabels(labels)
            ax.set_ylabel('Time')
            plt.title('Timing')

            plt.show(block=True)

        except ImportError:
            logging.critical("Cannot plot. Please ensure matplotlib "
                             "and networkx are installed.")

    def plot(self, property_name, block=True):
        """
        Plot the history of a property.

        Args:
            property_name (string): The name of the property to be plotted.

            block (bool): Stop the current process while displaying the plot.
                   False to continue the process. If false, make sure the
                   process does not end of its own accord (by putting in a
                   request for user input, for example) as the plot will
                   disappear.

        Returns:
            None

        Raises:

        """
        #TODO: Argument that specifies the type of nodes to which a property
        #      belongs. If it is empty, all nodes and links in the network will
        #      be checked for this property.

        #Import seaborn to prettify the graphs if possible
        try:
            import seaborn
        except:
            pass

        try:
            import matplotlib.pyplot as plt
            nodes_to_plot = []
            links_to_plot = []
            institutions_to_plot = []
            for n in self.nodes:
                if property_name in n.get_properties():
                    nodes_to_plot.append(n)
            for l in self.links:
                if property_name in l.get_properties():
                    if len(nodes_to_plot) > 0:
                        logging.warn("WARNING: Some nodes have the same property %s as this link %s"% (property_name, l.name))
                    links_to_plot.append(l)
            for i in self.institutions:
                if property_name in i.get_properties():
                    if len(nodes_to_plot) > 0 or len(links_to_plot) > 0:
                        logging.warn("WARNING: Some nodes and links have the same property %s as this institution (%s)"% (property_name, i.name))
                    institutions_to_plot.append(i)

            components_to_plot = nodes_to_plot + links_to_plot + \
                institutions_to_plot

            if len(components_to_plot) == 0:
                logging.warn("No components found with property %s"%property_name)
                return

            num_cols = min(len(components_to_plot), 5)
            num_rows = ((len(components_to_plot) - 1) / num_cols) + 1
            plt.figure(1)
            for i, component in enumerate(components_to_plot):
                plt.subplot(num_rows, num_cols, i + 1)
                plt.plot(component._history[property_name], 'r')
                plt.title('%s' % (component.name))
            plt.show(block=block)

        except ImportError:
            logging.critical("Cannot plot %s. Please ensure matplotlib "
                             "and networkx are installed."%property_name)

    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, self.name)

    def as_csv(self, target_dir):
        """
            Convert network into a set of hydra-compatible csv files.
        """

        raise NotImplementedError("Not implemented yet.")

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        #create target_dir/network.csv
        net_file = open(os.path.join(target_dir, 'network.csv'))
        #create target_dir/nodes.csv
        node_file = open(os.path.join(target_dir, 'nodes.csv'))
        #create target_dir/links.csv
        link_file = open(os.path.join(target_dir, 'links.csv'))
        #create target_dir/groups.csv
        group_file = open(os.path.join(target_dir, 'groups.csv'))
        #create target_dir/group_members.csv
        group_member_file = open(os.path.join(target_dir, 'group_members.csv'))
