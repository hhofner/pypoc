'''
This module contains the core Network class, which collects a list of objects
and creates a NetworkX object representation of the network. The main method of
the Network class loops through all network objects and calls their run() method.

Additionally, the Network class collects and holds a "NetworkData" object, which
contains all the metadata of the Network.
'''

__author__ = 'Hans Hofner'

import itertools
import logging
import random
import time
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
from tqdm import tqdm # Progress Bar
from scipy.spatial import distance
from pypoc.edgehandler import EdgeHandler
from pypoc.topology import Topology
from pypoc.node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode
from pypoc.qnode import QNode

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)

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

        self.data['drop_rate_list'] = []
        self.data['drop_rate_value'] = 0
        # Value of current packet drop rate
        self.data['packet_drop_rate_value'] = 0

        self.data['node_count_list'] = []

    def data_save_to_file(self, network, filename=None, data_filepath=None, config_file=None):
        '''
        Save all metadata to file, as well as all nodes data.
        :param network: PyPocNetwork object
        :return None:
        '''
        if filename is None:
            filename = f'{self.title}_{self.data["start_time_value"].strftime("%d%b%y_%H_%M_%S")}.csv'

        if data_filepath is None:
            data_filepath = f'./output_data/' + filename

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
        self.initialize_step_values()

        self.meta.title = configuration['title']
        self.meta.author = configuration['author']

        self.meta.area = (configuration['area']['width'], configuration['area']['height'])

        self.edge_handler = EdgeHandler(configuration)

        self.wanting_states = []

    def initialize_step_values(self):
        '''
        This method defines the step value for the
        network based on bandwidth and packet size, and then
        updates the value for all nodes.
        '''
        highest_bandwidth = None
        for edge in self.edges.data():
            try:
                bandwidth = edge[2]['Bandwidth']
            except KeyError:
                LOGGER.error(f'Could not find Bandwidth edge attribute for edge {edge}')
            else:
                if highest_bandwidth is None:
                    highest_bandwidth = edge[2]['Bandwidth']
                elif edge[2]['Bandwidth'] > highest_bandwidth:
                    highest_bandwidth = edge[2]['Bandwidth']

                # print(f'Setting Tick Value for edge {edge}')
                # print(f'Previous: {edge[2]["TickValue"]}')
                # Set the edges bandwidth value
                edge[2]['TickValue'] = self.packet_size/edge[2]['Bandwidth']
                # input(f'After: {edge[2]["TickValue"]}')

        self.step_value = self.packet_size/highest_bandwidth
        for node in self.nodes:
            node.step_value = self.step_value

        self.meta.data['step_value'] = self.step_value

    def update_throughput(self):
        try:
            overall_throughput = (self.meta.data['total_byte_count_value'] / (self.tick * self.meta.data['step_value']))
            self.meta.data['throughput_list'].append(overall_throughput)
            self.meta.data['throughput_value'] = overall_throughput
        except:
            raise

    def update_drop_rate(self):
        if Packet.dropped_count:
            overall_drop_rate = Packet.generated_count / Packet.dropped_count
        else:
            overall_drop_rate = 0
        self.meta.data['drop_rate_list'].append(overall_drop_rate)
        self.meta.data['drop_rate_value'] = overall_drop_rate

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

    def get_sat_node(self):
        sat_nodes = []
        for node in self.nodes:
            if node.name == 'leo-satellites':
                sat_nodes.append(node)

        return random.choice(sat_nodes)

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

    def collect_node_count(self):
        self.meta.data['node_count_list'].append(len(self.nodes))

    # TODO: This needs to be addressed...perhaps in EdgeHandler?
    def update_channel_loads(self):
        for edge in self.edges:
            n1, n2 = edge
            self[n1][n2]['Channel'] = len(n1.queue) + len(n2.queue)

    def request_state(self, node, memory_set):
        '''
        This adds the node to the "please record the state for this memory set  " list.
        '''
        if self.wanting_states:
            if node in self.wanting_states:
                self.wanting_states[node].append(memory_set)
            else:
                self.wanting_states[node] = [memory_set]
        else:
            self.wanting_states = {node: [memory_set]} 

    def _record_states(self):
        if not self.wanting_states:
            pass
        else:
            for node in self.wanting_states:
                # First get the state of the node
                node_state = node.get_state(self)
                # Then record the state at every memory_set
                for memory_set in self.wanting_states[node]:
                    memory_set['next_state'] = node_state

        self.wanting_states.clear()

    def preview(self):
        LOGGER.debug("Running network with these parameters")
        LOGGER.debug(f"Node count: {len(self.nodes)}")
        for node in self.nodes:
            LOGGER.debug(f'Node: {node} -- Type:{type(node)}')

        time.sleep(5)
    ###################################################################################################
    # Main Loop #######################################################################################
    ###################################################################################################
    def run_main_loop(self, minutes, **kwargs):
        self.preview()
        seconds = minutes * 60
        ticks = int(seconds / self.step_value)
        #answer = input(f'Please confirm run. {ticks} ticks, ok? ([y]/n) ')
        #if answer == 'n':
        #    print('Did not run'); return
        self.meta.data['start_time_value'] = datetime.now()
        LOGGER.debug(f'~~~~ Running {self.meta.title} for {ticks} time steps ~~~~')
        for self.tick in tqdm(range(1, ticks+1)):
            self.collect_node_count()
            # print(f'\n~~~~ TIME {self.tick} ~~~~\n')
            for node in self.nodes:
                # print(f'---->: {node} :<----')
                node.run(self)

            self.update_channel_loads()
            self.update_throughput()
            self.update_drop_rate()
            self.edge_handler.handle_edges(self)
            self._record_states()
            # print(f'Tick {self.tick}')
            # for edge in self.edges.data():
            #     print(edge)
            # input(',...')

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
        try:
            self.run_main_loop(minutes, **kwargs)
        except KeyboardInterrupt:
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


if __name__ == '__main__':
    print('Herein lies the Network class...')
