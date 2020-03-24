'''
This module contains the core Network class, which collects a list of objects
and creates a NetworkX object representation of the network. The main method of
the Network class loops through all network objects and calls their run() method.

Additionally, the Network class collects and holds a "NetworkData" object, which
contains all the metadata of the Network.
'''

__author__ = 'Hans Hofner'

import itertools
import itertools
import pickle
import csv
import os
from copy import copy
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import seaborn as sns
import pandas as pd
import numpy as np
import toml
from tqdm import tqdm
from scipy.spatial import distance
from topology import Topology
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode

configuration = toml.load('../config.toml')

class NetworkData:
    '''
    Contains specific InfoData objects on the Network.
    '''
    def __init__(self):
        '''
        Initialize data dictionary that is never to be accessed directly. Naming convention is
        to append either "_list" or "_value" to data key.
        '''
        self.name = ''
        self.author = ''
        self.data = {}

        # List of total network throughput value, per time.
        self.data['throughput_list'] = []

        # List of generated packets by any node, per time.
        self.data['generated_packet_list'] = []

        # Current total network throughput value.
        self.data['throughput_value'] = 0
        
        # Current step value for one `tick`
        self.data['step_value'] = 0

        # Current value of total generated packets.
        self.data['generated_packet_count_value'] = 0

        # Current value of total bytes sent
        self.data['total_byte_count_value'] = 0

        # Value of start time of data run
        self.data['start_time_value'] = 0

        # Value of end time of data run
        self.data['end_time_value'] = 0

        # Value of current packet drop rate
        self.data['packet_drop_rate_value'] = 0

    def data_save_to_file(self, network, filename=None):
        '''
        Save all metadata to file, as well as all nodes data.
        :param network: PyPocNetwork object
        :return None:
        '''
        if filename is None:
            filename = f'{self.name}_{self.data["start_time_value"]}.csv'

        with open(filename, mode='w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerow(['title', self.name])
            writer.writerow(['author', self.author])
            for key in self.data.keys():
                if isinstance(self.data[key], list):
                    writer.writerow([key] + self.data[key])
                else:
                    writer.writerow([key] + [self.data[key]])

class PyPocNetwork(nx.Graph):
    '''
    PyPocNetwork object that manages
    '''
    def initialize(self, packet_size):
        self.meta = NetworkData()  # for a fun naming thing; ie self.meta.data hehe
        self.meta.name

        self.packet_size = packet_size
        self._initialize_step_values()

    def _initialize_step_values(self):
        '''
        This method defines the step value for the
        network based on bandwidth and packet size, and then
        updates the value for all nodes.
        '''
        highest_bandwidth = self._find_highest_bandwidth()
        self.step_value = self.packet_size/highest_bandwidth
        for node in self.nodes:
            node.step_value = self.step_value
        
        self.meta.data['step_value'] = self.step_value

    #TODO:
    def _update_step_value(self, value=None):
        '''
        Updates the step value.
        '''
        pass

    def _find_highest_bandwidth(self):
        highest = None
        for edge in self.edges:
            v, u = edge
            if highest is None:
               highest = self[u][v]['Bandwidth']
            elif self[u][v]['Bandwidth'] < highest:
                highest = self[u][v]['Bandwidth']

        return highest

    def update_throughput(self):
        try:
            overall_throughput = (self.meta.data['total_byte_count_value'] / (self.tick * self.meta.data['step_value']))
            self.meta.data['throughput_list'].append(overall_throughput)
            self.meta.data['throughput_value'] = overall_throughput
        except:
            raise

    def get(self, key, node1, node2):
        return self[node1][node2][str(key)]

    def update_byte_count(self, packet):
        self.meta.data['total_byte_count_value'] += packet.size

    def reset(self):
        Packet.reset()

    def get_count_of(self, type_of_node):
        count = 0
        for node in self.nodes:
            if node.node_type == type_of_node:
                count += 1
        return count

    # TODO: This needs to be addressed...perhaps in EdgeHandler?
    def update_channel_loads(self):
        for edge in self.edges:
            n1, n2 = edge
            self[n1][n2]['Channel'] = len(n1.queue) + len(n2.queue)

    # TODO: This needs to be looked at.
    def update_channel_links(self):
        for node in self.nodes:
            if node.is_moving:
                print(f'Updating links for {node}')
                ''' Find distance between all other nodes'''
                to_remove_edges = []
                for edge in self.edges(node):
                    n1, n2 = edge
                    dist = distance.euclidean(n1.position, n2.position)
                    # input(f'Distance: {dist}\n\tn1 position: {n1.position}\n\tn2 position: {n2.position}')
                    ''' Then calculate the capacity for that link'''
                    capacity = signal_tools.calculate_capacity(dist)/8 # in BYTES
                    # input(f'Calculated Capacity: {capacity}')
                    '''Then Change the capacity'''
                    # self[n1][n2]['Bandwidth'] = capacity
                    # self.initialize_step_values()
                    if capacity < self.parameters['threshold_value']:
                        to_remove_edges.append((n1, n2))

                for node_pair in to_remove_edges:
                    u, v = node_pair
                    self.remove_edge(u, v)

    ###################################################################################################
    # Main Loop #######################################################################################
    ###################################################################################################
    def run_main_loop(self, minutes):
            seconds = minutes * 60
            ticks = int(seconds / self.step_value)
            input(f'Please confirm run. {ticks} ticks, ok? [y]')
            self.meta.data['start_time_value'] = datetime.now()
            print(f'~~~~ Running {self.meta.name} for {ticks} time steps.')
            for self.tick in tqdm(range(1, ticks+1)):
                # print(f'\n~~~~ TIME {self.tick} ~~~~\n')
                for node in self.nodes:
                    # print(f'---->: {node} :<----')
                    node.run(self)

                self.update_channel_loads()
                self.update_channel_links()
                self.update_throughput()

            # Postprocessing methods here #
            self.meta.data['end_time_value'] = datetime.now()

            print(f'########### FINISH ###########')
            print(f'\tGENERATED PACKETS: {Packet.generated_count}')
            print(f'\tARRIVED PACKETS: {Packet.arrived_count}')
            print(f'\tDROPPED PACKETS: {Packet.dropped_count}')
            print(f'\tPACKET LOSS RATE: {Packet.dropped_count/Packet.generated_count}')
            print(f'\tTIME DIFFERENCE: {self.meta.data["end_time_value"] - self.meta.data["start_time_value"]}')
            print(f'\tOVERALL THROUGHPUT: {self.meta.data["throughput_value"]/1e3} KBps')
            
            self.meta.data_save_to_file(None)

    ###################################################################################################
    # Main Interface Method ###########################################################################
    ###################################################################################################
    def run_network_with(self, config):
        '''
        :param minutes: Number of minutes to run the simulation for.
        :param edge_structure: list of edge tuples with bandwidth definition.
        :param packet_size: packet sizes to be sent.
        :param **kwargs: any other key-word arguments.
        :return: None

        '''

        # Get edge structure
        new = Topology(configuration)
        self.add_edges_from(new.topology)

        # Get packet size
        packet_size = configuration['global']['packet-size']
        self.initialize(packet_size)

        # Get minutes
        minutes = configuration['global']['minutes']
        self.run_main_loop(minutes)

        # Set title, author
        self.meta.title = configuration['title']
        self.meta.author = configuration['author']

if __name__ == '__main__':
    new = PyPocNetwork()
    new.run_network_with(configuration)