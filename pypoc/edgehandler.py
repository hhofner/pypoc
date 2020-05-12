import plotter
import numpy as np

'''
'''
__author__ = "Hans Hofner"

SAVE_TO_IMAGES = True

class EdgeHandler:
    '''
    Class responsible for handling `edges` of a networkX object based on a
    `foundation`, which is something that will define whether a link is
    valid or not.
    '''

    valid_foundations = {'distance'}
    def __init__(self, configuration):
        '''TODO Documentation
        '''
        edge_foundation = configuration['global']['link-foundation']

        if not edge_foundation in EdgeHandler.valid_foundations:
            raise Exception(f'Incorrect edge foundation {edge_foundation}; '
                            f'must be one of {EdgeHandler.valid_foundations}')

        self.edge_foundation = edge_foundation

        self._config = configuration

        self.set_area((self._config['area']['width'], self._config['area']['height']))

        self._connections_for = {}
        self._downlink_bandwidth_for = {}
        for node in self._config['nodes'].keys():
            self._connections_for[node] = \
                self._config['nodes'][node]['connected-to']
            self._downlink_bandwidth_for[node] = \
                self._config['nodes'][node]['params']['downlink-bandwidth']

        self.image_count = 0

    # Main Entrance Method
    def handle_edges(self, networkx_object):
        '''TODO Documentation
        '''
        # "Handle" edges every 50 ticks
        if not networkx_object.tick % 30:
            if self.edge_foundation == 'distance':
                self._handle_edges_based_on_distance(networkx_object)

            # reset important edge values of a node
            networkx_object.initialize_step_values()
            self._reset_node_values(networkx_object)

            if SAVE_TO_IMAGES:
                if not networkx_object.tick % 100:
                    self._save_images(networkx_object)

    def _handle_edges_based_on_distance(self, networkx_object):
        '''TODO Documentation
        '''
        print('Handling Edges based on distance...')
        try:
            self.area
        except:
            raise Exception(f'To use distance foundation, please set the area with `set_area()`.')

        edge_list = []
        for node in networkx_object.nodes:  # Go through every node
            viable_connections = self._connections_for[node.name]  # Get list of nodes it can connect to
            for node2 in networkx_object.nodes:
                for vn in viable_connections:
                    if self._is_distance_ok(node, node2) and not node is node2 and node2.name == vn:
                        if not networkx_object.has_edge(node, node2):
                            new_connection =\
                                (node, node2, {'Bandwidth': self._downlink_bandwidth_for[node.name],
                                               'TickValue': None,
                                               'Channel': 0})
                            print(f'Adding new connection {new_connection}')
                            edge_list.append(new_connection)
                    elif not self._is_distance_ok(node, node2) and networkx_object.has_edge(node, node2):
                        networkx_object.remove_edge(node, node2)
                        print(f'Removing edge: {node} -> {node2}')
        if not len(edge_list) == 0:
            networkx_object.add_edges_from(edge_list)

    def _reset_node_values(self, networkx_object):
        for node in networkx_object.nodes:
            node.reset_values(networkx_object)

    def _is_distance_ok(self, node, node2):
        '''TODO Documentation
        '''
        def distance(node1, node2):
            a = np.array(node1.position)
            b = np.array(node2.position)
            return np.linalg.norm(a-b)

        # input(f'Distance Between {node} and {node2} is {distance(node, node2)}')
        if node.node_type == node2.node_type:
            return True

        if node.node_type == 1 or node2.node_type == 1:
            if distance(node, node2) < 50:  #TODO: Distance!!!! Change!!! PLS
                return True

        if node.name == 'leo-satellites' or node2.name == 'leo-satellites':
            if distance(node, node2) < 2000:
                return True

        return False

    def set_area(self, area):
        '''TODO Documentation
        '''
        self.area = area

    def _save_images(self, networkx_object):
        filepath = 'gif_images/current_' + str(self.image_count) + '.png'
        self.image_count += 1
        kwargs = {'tick_val': networkx_object.tick}
        plotter.save_network_graph_image(networkx_object, filepath, **kwargs)
