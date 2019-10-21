import networkx as nx
import generating_node
import simple_channel
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import copy
from collections import defaultdict
import numpy as np


def run_network_for(time_steps, time_equivalent, topology_func,
                    num_of_nodes):
    network = nx.Graph()
    ''' Create Channels'''

    ''' Create nodes and their connections '''
    print(f'#### Creating Edge Connections ####')
    ebunch = topology_func(num_of_nodes, time_equivalent)

    network.add_edges_from(ebunch)

    '''############### RUN LOOP #################'''
    steps = time_steps

    print('#### Starting network ####')
    while steps > 0:
        print(f'///// t={time_steps - steps} /////')

        # RUNNING NETWORK ####
        for node in network.nodes:
            node.generate(network)

        for edge in network.edges:
            n1, n2 = edge
            channel_list = network[n1][n2]['Channel']  # list of channel obj

            n1.transmit_to(channel_list)
            n2.transmit_to(channel_list)

            for_n1 = []
            for_n2 = []
            for chan in network[n1][n2]['Channel']:
                for_n1 += chan.get_packets(src=n2, dest=n1)
                for_n2 += chan.get_packets(src=n1, dest=n2)
                chan.update()

            print(f'len of for_n1 = {len(for_n1)}')
            print(f'len of for_n2 = {len(for_n2)}')

            n1.receive(for_n1)
            n2.receive(for_n2)

            # Update weights
            network[n1][n2]['Weight'] += (len(for_n1) + len(for_n2))

        steps = steps - 1
    '''##########################################'''
    print('#### Finished ####')

    ''' Data Structures'''
    network_data = defaultdict(None)

    # Collect all data from the nodes
    for node in network.nodes():
        network_data[str(node)] = node.metadata

    # network_data[str(main_channel1)] = main_channel1.metadata
    network_data['dropped_count'] = generating_node.Packet.dropped_count
    network_data['arrived_count'] = generating_node.Packet.arrived_count
    generating_node.Packet.reset()

    # Collect all data from channels
    # for edge in network.edges:
    #     n1, n2 = edge
    #     network_data[edge] = network[n1][n2]['Channel']

    for edge in network.edges:
        n1, n2 = edge
        print(f'Edge {n1}---{n2}:')
        for chan in network[n1][n2]['Channel']:
            for key in chan.data.keys():
                print(f'{key}: {len(chan.data[key])}')


    return network_data


def sagin_topology(number_of_nodes, time_equivalent):
    '''
    Instantiate nodes and create the corresponding connections.

    :param number_of_nodes: Int w/ how many nodes in topology
    :param channel_list:
    '''

    print(f'Creating {number_of_nodes} Nodes')

    receiving_nodes = []
    for _ in range(4):
        new = generating_node.ImprovedMultipleChannelNode(time_equivalent,
                                                          packet_size=None,
                                                          queue_size=1000,
                                                          transmit_rate=0,
                                                          gen_rate=0,
                                                          type='dest',
                                                          channel_interface_list=['main'])
        receiving_nodes.append(new)

    level_one_relays = []
    for _ in range(8):
        new = generating_node.ImprovedMultipleChannelNode(time_equivalent,
                                                          packet_size=None,
                                                          queue_size=5000,
                                                          transmit_rate=1250,
                                                          gen_rate=0,
                                                          type='lvl1',
                                                          channel_interface_list=['main'])
        level_one_relays.append(new)

    level_two_relays = []
    for _ in range(2):
        new = generating_node.ImprovedMultipleChannelNode(time_equivalent,
                                                          packet_size=None,
                                                          queue_size=5000,
                                                          transmit_rate=12500,
                                                          gen_rate=0,
                                                          type='lvl2',
                                                          channel_interface_list=['main'])
        level_two_relays.append(new)

    transmit_nodes = []
    for _ in range(4):
        new_node = generating_node.ImprovedMultipleChannelNode(time_equivalent,
                                                               packet_size=1,
                                                               queue_size=500,
                                                               transmit_rate=1250,
                                                               gen_rate=1250,
                                                               destinations=receiving_nodes,
                                                               type='src',
                                                               channel_interface_list=['main'])
        transmit_nodes.append(new_node)

    ''' Create connections '''
    main_chan = simple_channel.SimpleChannel(name='main',
                                bandwidth='12500',
                                time_equivalent=time_equivalent)
    ebunch = []  # list of edge-tuples i.e. [(n1, n2, {})]
    for tn in transmit_nodes:
        for rn in level_one_relays[:4]:
            temp = (tn, rn, {'Weight': 1, 'Channel': [copy.deepcopy(main_chan)]})
            ebunch.append(temp)

    for dn in receiving_nodes:
        for rn in level_one_relays[4:]:
            temp = (dn, rn, {'Weight': 1, 'Channel': [copy.deepcopy(main_chan)]})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn2 in level_two_relays:
            temp = (rn1, rn2, {'Weight': 1, 'Channel': [copy.deepcopy(main_chan)]})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn12 in level_one_relays:
            if rn1 is not rn12:
                temp = (rn1, rn2, {'Weight': 1, 'Channel': [copy.deepcopy(main_chan)]})
                ebunch.append(temp)

    return ebunch


def show_data_overview(data, nodes=None):
    for key in data.keys():
        print(f'{key}')
        try:
            for k in data[key].keys():
                print(f'\t{k}')
                if type(data[key][k]) is list:
                    # Print length of list
                    print(f'\t\t length: {len(data[key][k])}')
                else:
                    print(f'\t\t{data[key][k]}')
        except AttributeError as err:
            print(f'\t{key}')
            print(f'\t\t{data[key]}')


if __name__ == '__main__':
    data = run_network_for(time_steps=30, time_equivalent=0.001,
                           topology_func=sagin_topology,
                           num_of_nodes=6)

    print('################### DATA ###################')
    show_data_overview(data)
