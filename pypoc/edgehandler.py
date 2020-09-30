import pypoc.plotter
import numpy as np

import logging

from pypoc.mobility import MobilityEnum
from pypoc.node import RestrictedNode
'''
'''
__author__ = "Hans Hofner"

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

SAVE_TO_IMAGES = False

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

        self.last_increase_tick = 0
        self.increase_length = None
        self.increase_rate = self._config['global']['increase-rate']

    # Main Entrance Method
    def handle_edges(self, networkx_object):
        '''TODO Documentation
        '''
        # "Handle" edges every 50 ticks
        if not networkx_object.tick % 10:
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
        #print('Handling Edges based on distance...')
        try:
            self.area
        except:
            raise Exception(f'To use distance foundation, please set the area with `set_area()`.')

        edge_list = []
        LOGGER.debug(f'BEFORE-Number of nodes: {len(list(networkx_object.nodes))}')
        self._increase_source_nodes(networkx_object)
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
                            #print(f'Adding new connection {new_connection}')
                            edge_list.append(new_connection)
                    elif not self._is_distance_ok(node, node2) and networkx_object.has_edge(node, node2):
                        networkx_object.remove_edge(node, node2)
                        #print(f'Removing edge: {node} -> {node2}')
        if not len(edge_list) == 0:
            networkx_object.add_edges_from(edge_list)

        LOGGER.debug(f'AFTER-Number of nodes: {len(list(networkx_object.nodes))}')

    def _increase_source_nodes(self, networkx_object):
        self.increase_length = (self._config['global']['increase-time']*60) / networkx_object.step_value
        if networkx_object.tick - self.last_increase_tick > self.increase_length:
            LOGGER.debug('Increasing source nodes')
            # Increase the source nodes
            self.last_increase_tick = networkx_object.tick
            node_type = 0
            position = self.get_position('ue-random', (self._config['area']['width'], self._config['area']['width']))
            movement = MobilityEnum.get_movement(self._config['nodes']['src-nodes']['movement'])
            params = self._config['nodes']['src-nodes']['params']
            packet_size = self._config['global']['packet-size']

            nodes = []
            for _ in range(self.increase_rate):
                new_src_node = RestrictedNode(node_type=node_type,
                                            step_value=0,
                                            mobility_model=movement,
                                            packet_size=packet_size,
                                            gen_rate=params['generation-rate'],
                                            max_buffer_size=params['buffer-size'])
                new_src_node.set_name('src-nodes')
                nodes.append(new_src_node)
            
            networkx_object.add_nodes_from(nodes)
            LOGGER.debug(f"Added nodes {nodes}")

    def get_position(self, p_arg, area):
        if p_arg == 'ue-random':
            return self._ue_random(area)
        elif p_arg == 'none':
            return (0,0,0)
        else:
            x= int(p_arg[count][0])
            y= int(p_arg[count][1])
            z= int(p_arg[count][2])
            return (x,y,z)

    def _ue_random(self, area):
        x, y = np.random.normal(size=(2,)) * (area[0]/3, area[1]/3)
        x = min(x, area[0])
        y = min(y, area[1])
        return (x, y, 0)

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

        if node.name == 'q-stations' or node2.name == 'q-stations':
            return True

        if node.name == 'base-stations' and node2.name == 'base-stations':
            return True

        if node.name == 'base-stations' or node2.name == 'base-stations':
            if distance(node, node2) <= 55:
                return True
        
        if node.name == 'uav-base-stations' or node2.name == 'uav-base-stations':
            if distance(node, node2) <= 45:
                return True
        
        if node.name  == 'leo-satellites' or node2.name == 'leo-satellites':
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
