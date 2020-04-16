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


class NetworkData:
    def __init__(self):
        '''
        Initialize data dictionary that is never to be accessed directly. Naming convention is
        to append either "_list" or "_value" to data key.
        '''
        self.title = ''
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

    def data_save_to_file(self, network, filename=None, data_filepath=None, config_file=None):
        '''
        Save all metadata to file, as well as all nodes data.
        :param network: PyPocNetwork object
        :return None:
        '''
        if filename is None:
            filename = f'{self.title}_{self.data["start_time_value"].strftime("%d%b%y_%H_%M_%S")}.csv'

        if data_filepath is None:
            data_filepath = f'./simulation_data/' + filename

        with open(data_filepath, mode='w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerow(['title', self.title])
            writer.writerow(['author', self.author])
            for key in self.data.keys():
                if isinstance(self.data[key], list):
                    writer.writerow([key] + self.data[key])
                else:
                    writer.writerow([key] + [self.data[key]])


class PyPocNetwork(nx.DiGraph):
    '''
    PyPocNetwork object that manages
    '''
    def initialize(self, configuration):
        self.meta = NetworkData()  # for a fun naming thing; ie self.meta.data hehe

        self.packet_size = configuration['global']['packet-size']
        self._initialize_step_values()

        self.meta.title = configuration['title']
        self.meta.author = configuration['author']

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
        for edge in self.edges.data():
            try:
                bandwidth = edge[2]['Bandwidth']
            except KeywordError:
                print(f'Could not find Bandwidth edge attribute for edge {e}')
            else:
                if highest is None:
                    highest = bandwidth
                elif bandwidth > highest:
                    highest = bandwidth

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

    def collect_node_data(self):
        '''
        Collect all node data populating it into self.meta.data dictionary.
        '''
        print('Collecting node data...')
        for node in self.nodes:
            for key in node.data.keys():
                self.meta.data[f'{node}_{key}'] = node.data[key]

    def collect_packet_data(self):
        '''
        Iterate through all packets (dropped ones, too) and collect their data into file.
        '''
        # In theory, there should be no double reference to the same packet...
        for node in self.nodes:
            for dropped_packet in node.data['dropped_packets']:
                self.meta.data[f'{dropped_packet}_path'] = dropped_packet.path_nodes['past']
                self.meta.data[f'{dropped_packet}_born_tick'] = dropped_packet.born_tick
                self.meta.data[f'{dropped_packet}_died_tick'] = dropped_packet.died_tick
            if node.node_type is 2:
                for packet in node.queue:
                    # Path taken by Packet
                    self.meta.data[f'{packet}_path'] = packet.path_nodes['past']
                    self.meta.data[f'{packet}_born_tick'] = packet.born_tick
                    self.meta.data[f'{packet}_died_tick'] = packet.died_tick

        self.meta.data['packet_drop_value'] = Packet.dropped_count
        self.meta.data['packet_arrive_value'] = Packet.arrived_count
        self.meta.data['packet_generated_value'] = Packet.generated_count

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
    def run_main_loop(self, minutes, **kwargs):
        seconds = minutes * 60
        ticks = int(seconds / self.step_value)
        answer = input(f'Please confirm run. {ticks} ticks, ok? ([y]/n) ')
        if answer == 'n':
            print('Did not run'); return
        self.meta.data['start_time_value'] = datetime.now()
        print(f'~~~~ Running {self.meta.title} for {ticks} time steps ~~~~')
        for self.tick in tqdm(range(1, ticks+1)):
            # print(f'\n~~~~ TIME {self.tick} ~~~~\n')
            for node in self.nodes:
                # print(f'---->: {node} :<----')
                node.run(self)

            self.update_channel_loads()
            self.update_channel_links()
            self.update_throughput()

        if 'filename' in kwargs.keys():
            simulation_filename = kwargs['filename']
        # Postprocessing methods here #
        self.meta.data['end_time_value'] = datetime.now()
        self.collect_node_data()
        self.collect_packet_data()
        self.meta.data_save_to_file(self, simulation_filename)

        print(f'########### FINISH ###########')
        print(f'\tGENERATED PACKETS: {Packet.generated_count}')
        print(f'\tARRIVED PACKETS: {Packet.arrived_count}')
        print(f'\tDROPPED PACKETS: {Packet.dropped_count}')
        print(f'\tPACKET LOSS RATE: {Packet.dropped_count/Packet.generated_count}')
        print(f'\tTIME DIFFERENCE: {self.meta.data["end_time_value"] - self.meta.data["start_time_value"]}')
        print(f'\tOVERALL THROUGHPUT: {self.meta.data["throughput_value"]/1e3} KBps')

    ###################################################################################################
    # Main Interface Method ###########################################################################
    ###################################################################################################
    def run_network_with(self, configuration, **kwargs):
        '''
        #TODO: Documentation
        :return: None

        '''

        # Get edge structure
        new = Topology(configuration)
        self.add_edges_from(new.topology)

        self.initialize(configuration)

        # Get minutes
        minutes = configuration['global']['minutes']
        self.run_main_loop(minutes, **kwargs)


if __name__ == '__main__':
    print('Herein lies the Network class...')
