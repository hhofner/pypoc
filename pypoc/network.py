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
from tqdm import tqdm # Progress Bar
from scipy.spatial import distance
from edgehandler import EdgeHandler
from topology import Topology
from network_data import NetworkData
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode


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
                print(f'Could not find Bandwidth edge attribute for edge {edge}')
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

    ###################################################################################################
    # Main Loop #######################################################################################
    ###################################################################################################
    def run_main_loop(self, minutes, **kwargs):
        seconds = minutes * 60
        ticks = int(seconds / self.step_value)
        #answer = input(f'Please confirm run. {ticks} ticks, ok? ([y]/n) ')
        #if answer == 'n':
        #    print('Did not run'); return
        self.meta.data['start_time_value'] = datetime.now()
        print(f'~~~~ Running {self.meta.title} for {ticks} time steps ~~~~')
        for self.tick in tqdm(range(1, ticks+1)):
            # print(f'\n~~~~ TIME {self.tick} ~~~~\n')
            for node in self.nodes:
                # print(f'---->: {node} :<----')
                node.run(self)

            self.update_channel_loads()
            self.update_throughput()
            self.edge_handler.handle_edges(self)

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
        self.run_main_loop(minutes, **kwargs)


if __name__ == '__main__':
    print('Herein lies the Network class...')
