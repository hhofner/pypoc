'''
This module provides a class and methods to build the users desired topology.
The class is populated by reading the configuration file `setup.toml`.
'''

import itertools
import random
import argparse
import numpy as np
import toml
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode
from mobility import ellipse_movement, straight_line


class Topology:
    def __init__(self, configuration):
        print('Initializing topology configuration...')
        packet_size = configuration['global']['packet-size']
        
        self.node_dict = {}  # Dict of TYPE of Nodes (src-node, etc)
        print('Creating node objects...')
        for node in configuration['nodes'].keys():
            self.node_dict[node] = []  # Make an entry for different type of node
            node_type = configuration['nodes'][node]['type']
            count = configuration['nodes'][node]['count']
            position = configuration['nodes'][node]['position']
            movement = configuration['nodes'][node]['movement']
            parameters = configuration['nodes'][node]['params']

            # Create nodes
            for _ in range(count):
                new_node = RestrictedNode(node_type=node_type,
                                          step_value=0,
                                          mobility_model=movement,
                                          packet_size=packet_size,
                                          gen_rate=parameters['generation-rate'],
                                          max_buffer_size=parameters['buffer-size'])
                self.node_dict[node].append(new_node)

        # Build connections
        if configuration['global']['link-foundation'] == 'distance':
            self.create_distance_links(configuration)

    def create_distance_links(self, configuration):
        '''
        Create a list of tuples that represent a link between two nodes.
        The parameters of the links are represented as a dictionary. Sets the 
        `self.topology` variable. 

        :param configuration: dict, topology configuration
        :return: None
        '''
        # TODO: Specifying uplink + downlink bandwidth --> for now just use downlink
        if len(self.node_dict) == 0:
            raise Exception('No available nodes to make links.')

        def is_distance_ok(node, node2):
            if distance(node, node2) < 1:
                return True
            else:
                return False

        print('Creating links between nodes...')
        edge_list = []

        connections_for = {}
        uplink_bandwidth_for = {}
        downlink_bandwidth_for = {}
        # Fetch info on what nodes connect to what nodes
        for node in configuration['nodes'].keys():
            connections_for[node] = configuration['nodes'][node]['connected-to']
            downlink_bandwidth_for[node] = configuration['nodes'][node]['params']['downlink-bandwidth']
            uplink_bandwidth_for[node] = configuration['nodes'][node]['params']['uplink-bandwidth']

        # Start making connections
        for node_key in self.node_dict:
            viable_connections = connections_for[node_key]  # Get list of nodes it can connect to
            for node in self.node_dict[node_key]:
                for vn in viable_connections:
                    for node2 in self.node_dict[vn]:
                        if is_distance_ok(node, node2):
                            new_connection = (node, node2, {'Bandwidth': downlink_bandwidth_for[node_key]})
                            edge_list.append(new_connection)

        self.topology = edge_list


def distance(node1, node2):
    a = np.array(node1.position)
    b = np.array(node2.position)
    return np.linalg.norm(a-b)

###################################################################################################

###################################################################################################
# Drawing Helper Methods #
def get_sagin_positional(network):
    pos_dict = {}
    whatever = [(1,0), (2,0), (3,0), (4,0), (1,1), (2,1), (3,1), (4,1), (3, 2), (6, 2), (5, 1), (6, 1), (7, 1), (8, 1), (5, 0), (6, 0), (7, 0), (8, 0)]
    for node in network:
        print(node.id)
        pos_dict[node] = whatever[node.id]

    return pos_dict

if __name__ == '__main__':
    configuration = toml.load('../config.toml')
    print('testing topology')
    new = Topology(configuration)
    print(new.topology)
