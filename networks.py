'''
networks.py -- This module contains different types of networks that can
be run.

Author: Hans Hofner
'''
import copy
import nodes
import methods
import simple_channel
import networkx as nx
import matplotlib.pyplot as plt

from collections import defaultdict


def simple_network(time_steps, topology_func):
    '''
    A simple network that uses no channels.

    :param time_steps: Int, how many time steps to run the network for.
    :param topology_func: A function that returns an ebunch of a network.
    :return network_data:
    '''
    network = nx.Graph()
    ''' Create Channels'''

    ''' Create nodes and their connections '''
    print(f'#### Creating Edge Connections ####')
    ebunch = topology_func(1, 1)

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
            chan = network[n1][n2]['Channel']

            n1.transmit_to(chan)
            n2.transmit_to(chan)

            for_n1 = chan.get_packets(src=n2, dest=n1)
            for_n2 = chan.get_packets(src=n1, dest=n2)
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
        network_data[str(node)] = node.data

    # network_data[str(main_channel1)] = main_channel1.metadata
    network_data['dropped_count'] = methods.Packet.dropped_count
    network_data['arrived_count'] = methods.Packet.arrived_count
    network_data['generated_count'] = methods.Packet.generated_count
    methods.Packet.reset()

    # Collect all data from channels
    # for edge in network.edges:
    #     n1, n2 = edge
    #     network_data[edge] = network[n1][n2]['Channel']

    # for edge in network.edges:
    #     n1, n2 = edge
    #     print(f'Edge {n1}---{n2}:')
    #     for chan in network[n1][n2]['Channel']:
    #         for key in chan.data.keys():
    #             print(f'{key}: {len(chan.data[key])}')

    return network_data


def sagin_topology(number_of_nodes, time_equivalent):
    '''
    Instantiate nodes and create the corresponding connections.

    :param number_of_nodes: Int w/ how many nodes in topology
    :param channel_list:
    '''

    print(f'Creating {number_of_nodes} Nodes')

    receiving_nodes = []
    for _ in range(3):
        new = nodes.SimpleNode(0, 0, 2000, type='dest')
        receiving_nodes.append(new)

    level_one_relays = []
    for _ in range(8):
        new = nodes.SimpleNode(1, 0, 500, type='lvl1')
        level_one_relays.append(new)

    level_two_relays = []
    for _ in range(2):
        new = nodes.SimpleNode(1, 0, 500, type='lvl2')
        level_two_relays.append(new)

    transmit_nodes = []
    for _ in range(3):
        new = nodes.SimpleNode(1, 1, 2000, type='src', dest=receiving_nodes)
        transmit_nodes.append(new)

    ''' Create connections '''
    main_chan = simple_channel.SimpleChannel(name='main',
                                             bandwidth='12500',
                                             time_equivalent=time_equivalent)
    ebunch = []  # list of edge-tuples i.e. [(n1, n2, {})]
    for tn in transmit_nodes:
        for rn in level_one_relays[:3]:
            temp = (tn, rn, {'Weight': 1, 'Channel': copy.deepcopy(main_chan)})
            ebunch.append(temp)

    for dn in receiving_nodes:
        for rn in level_one_relays[3:]:
            temp = (dn, rn, {'Weight': 1, 'Channel': copy.deepcopy(main_chan)})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn2 in level_two_relays:
            temp = (rn1, rn2, {'Weight': 1, 'Channel': copy.deepcopy(main_chan)})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn12 in level_one_relays:
            if rn1 is not rn12:
                temp = (rn1, rn2, {'Weight': 1, 'Channel': copy.deepcopy(main_chan)})
                ebunch.append(temp)

    return ebunch


data = simple_network(20, sagin_topology)

fig, (ax1, ax2) = plt.subplots(2, 1)

for key in data.keys():
    if 'src' in key:
        generated_counts = []
        for l in data[key]['generate_packet_list']:
            generated_counts.append(len(l))
        ax1.plot(generated_counts)

ax2.bar(['Generated', 'Arrived', 'Dropped'],
        [data['generated_count'],
         data['arrived_count'],
         data['dropped_count']])

plt.show()
