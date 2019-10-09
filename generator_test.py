import networkx as nx
import generating_node
import simple_channel
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import defaultdict
import numpy as np

def run_network_for(ground_nodes, air_nodes, space_nodes, t_steps, time_equivalent):
    network = nx.Graph()
    ''' Create nodes'''
    receiving_nodes = []
    for _ in range(ground_nodes//2):
        new = generating_node.Node(time_equivalent, packet_size=None, queue_size=1000, transmit_rate=0, gen_rate=0,
                                    type='dest')
        receiving_nodes.append(new)

    level_one_relays = []
    for _ in range(air_nodes):
        new = generating_node.Node(time_equivalent, packet_size=None, queue_size=5000, transmit_rate=np.random.normal(125000), gen_rate=0,
                                    type='lvl1')
        level_one_relays.append(new)

    level_two_relays = []
    for _ in range(space_nodes):
        new = generating_node.Node(time_equivalent, packet_size=None, queue_size=5000, transmit_rate=np.random.normal(1250000), gen_rate=0,
                                    type='lvl2')
        level_two_relays.append(new)

    transmit_nodes = []
    for _ in range(ground_nodes - ground_nodes//2):
        new_node = generating_node.Node(time_equivalent, packet_size=1, queue_size=int(8e7), transmit_rate=np.random.randint(125, 1250), gen_rate=np.random.normal(125),
                                        destinations=receiving_nodes,  type='src')
        transmit_nodes.append(new_node)

    ''' Create connections '''
    channels = []
    main_channel1 = simple_channel.Channel(name='main1', time_step=time_equivalent, bandwidth=10e9, sinr=40)
    main_channel2 = simple_channel.Channel(name='main2', time_step=time_equivalent, bandwidth=10e9, sinr=40)

    wimax = simple_channel.Channel(name='wimax', time_step=time_equivalent, bandwidth=10e9, sinr=40)

    ebunch = [] #list of edge-tuples
    half1 = len(level_one_relays)//2
    for tn in transmit_nodes:
        for rn in level_one_relays[:half1]:
            temp = (tn, rn, {'Weight' : 1, 'Channel': main_channel1})
            ebunch.append(temp)

    for dn in receiving_nodes:
        for rn in level_one_relays[half1:]:
            temp = (dn, rn, {'Weight': 1, 'Channel': main_channel1})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn2 in level_two_relays:
            temp = (rn1, rn2, {'Weight': 1, 'Channel': main_channel1})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn12 in level_one_relays:
            if not rn1 is rn12:
                temp = (rn1, rn2, {'Weight': 1, 'Channel': main_channel1})
                ebunch.append(temp)

    network.add_edges_from(ebunch)

    ''' Data Structures'''
    network_data = defaultdict(None)

    '''############### RUN LOOP #################'''
    time_steps = t_steps

    print('Starting network...')
    while time_steps > 0:

        #### RUNNING NETWORK ####
        for node in network.nodes:
            node.generate(network)

            # Transmit to channel
            #TODO: Idea, pass channel name to transmit (looping through available channels)
            main_channel1.transmit_access(node.transmit())

        # 'Access' the packets in the channel
        for edge in network.edges:
            n1, n2 = edge
            for_n1 = network[n1][n2]['Channel'].receive_access(n2, n1)
            for_n2 = network[n1][n2]['Channel'].receive_access(n1, n2)

            n1.receive(for_n1)
            n2.receive(for_n2)

            #Update weights
            network[n1][n2]['Weight'] += (len(for_n1) + len(for_n2))


        #### RUNNING NETWORK ####
        time_steps = time_steps - 1
    '''##########################################'''
    print('Finished')
    # Collect all data from the nodes
    for node in network.nodes():
        network_data[str(node)] = node.metadata

    network_data[str(main_channel1)] = main_channel1.metadata
    network_data['dropped_count'] = generating_node.Packet.dropped_count
    network_data['arrived_count'] = generating_node.Packet.arrived_count
    generating_node.Packet.reset()
    return network_data

def run_multiple_chan_network_for(ground_nodes, air_nodes, space_nodes, t_steps, time_equivalent):
    network = nx.Graph()
    ''' Create Channels'''
    channel_list = []
    channel_list.append(simple_channel.Channel(name='main1', time_step=time_equivalent, bandwidth=60e6, sinr=1000))
    channel_list.append(simple_channel.Channel(name='main2', time_step=time_equivalent, bandwidth=30e6, sinr=1000))
    channel_list.append(simple_channel.Channel(name='wimax', time_step=time_equivalent, bandwidth=5e6, sinr=1000))
    channel_list.append(simple_channel.Channel(name='wifi', time_step=time_equivalent, bandwidth=100e3, sinr=1000))

    ''' Create nodes'''
    receiving_nodes = []
    for _ in range(ground_nodes//2):
        new = generating_node.MultipleChannelNode(time_equivalent, packet_size=None, queue_size=1000, transmit_rate=0, gen_rate=0,
                                    type='dest', channel_interface_list=channel_list)
        receiving_nodes.append(new)

    level_one_relays = []
    for _ in range(air_nodes):
        new = generating_node.MultipleChannelNode(time_equivalent, packet_size=None, queue_size=5000, transmit_rate=1250, gen_rate=0,
                                    type='lvl1', channel_interface_list=channel_list)
        level_one_relays.append(new)

    level_two_relays = []
    for _ in range(space_nodes):
        new = generating_node.MultipleChannelNode(time_equivalent, packet_size=None, queue_size=5000, transmit_rate=12500, gen_rate=0,
                                    type='lvl2', channel_interface_list=channel_list)
        level_two_relays.append(new)

    transmit_nodes = []
    for _ in range(ground_nodes - ground_nodes//2):
        new_node = generating_node.MultipleChannelNode(time_equivalent, packet_size=1, queue_size=500, transmit_rate=1250, gen_rate=1250,
                                        destinations=receiving_nodes,  type='src', channel_interface_list=channel_list)
        transmit_nodes.append(new_node)

    ''' Create connections '''

    ebunch = [] #list of edge-tuples
    half1 = len(level_one_relays)//2
    for tn in transmit_nodes:
        for rn in level_one_relays[:half1]:
            temp = (tn, rn, {'Weight' : 1, 'Channel': channel_list})
            ebunch.append(temp)

    for dn in receiving_nodes:
        for rn in level_one_relays[half1:]:
            temp = (dn, rn, {'Weight': 1, 'Channel': channel_list})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn2 in level_two_relays:
            temp = (rn1, rn2, {'Weight': 1, 'Channel': channel_list})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn12 in level_one_relays:
            if not rn1 is rn12:
                temp = (rn1, rn2, {'Weight': 1, 'Channel': channel_list})
                ebunch.append(temp)

    network.add_edges_from(ebunch)

    ''' Data Structures'''
    network_data = defaultdict(None)

    '''############### RUN LOOP #################'''
    time_steps = t_steps

    print('Starting network...')
    while time_steps > 0:

        #### RUNNING NETWORK ####
        for node in network.nodes:
            node.generate(network)

            # Transmit to channel
            #TODO: Idea, pass channel name to transmit (looping through available channels)
            node.transmit(channel_list)

        # 'Access' the packets in the channel
        for edge in network.edges:
            n1, n2 = edge
            for_n1 = []
            for_n2 = []
            for chan in network[n1][n2]['Channel']:
                for_n1 += chan.receive_access(n2, n1)
                for_n2 += chan.receive_access(n1, n2)

            n1.receive(for_n1)
            n2.receive(for_n2)

            #Update weights
            network[n1][n2]['Weight'] += (len(for_n1) + len(for_n2))

        print(time_steps)
        #### RUNNING NETWORK ####
        time_steps = time_steps - 1
    '''##########################################'''
    print('Finished')
    # Collect all data from the nodes
    for node in network.nodes():
        network_data[str(node)] = node.metadata

    # network_data[str(main_channel1)] = main_channel1.metadata
    network_data['dropped_count'] = generating_node.Packet.dropped_count
    network_data['arrived_count'] = generating_node.Packet.arrived_count
    generating_node.Packet.reset()
    return network_data

def run_improved_multiple_chan_network_for(ground_nodes, air_nodes, space_nodes, t_steps, time_equivalent):
    network = nx.Graph()
    ''' Create Channels'''
    channel_list = []
    channel_list.append(simple_channel.Channel(name='main1', time_step=time_equivalent, bandwidth=60e6, sinr=1000))
    channel_list.append(simple_channel.Channel(name='main2', time_step=time_equivalent, bandwidth=30e6, sinr=1000))
    channel_list.append(simple_channel.Channel(name='wimax', time_step=time_equivalent, bandwidth=5e6, sinr=1000))
    channel_list.append(simple_channel.Channel(name='wifi', time_step=time_equivalent, bandwidth=100e3, sinr=1000))

    ''' Create nodes'''
    receiving_nodes = []
    for _ in range(ground_nodes//2):
        new = generating_node.ImprovedMultipleChannelNode(time_equivalent, packet_size=None, queue_size=1000, transmit_rate=0, gen_rate=0,
                                    type='dest', channel_interface_list=channel_list)
        receiving_nodes.append(new)

    level_one_relays = []
    for _ in range(air_nodes):
        new = generating_node.ImprovedMultipleChannelNode(time_equivalent, packet_size=None, queue_size=5000, transmit_rate=1250, gen_rate=0,
                                    type='lvl1', channel_interface_list=channel_list)
        level_one_relays.append(new)

    level_two_relays = []
    for _ in range(space_nodes):
        new = generating_node.ImprovedMultipleChannelNode(time_equivalent, packet_size=None, queue_size=5000, transmit_rate=12500, gen_rate=0,
                                    type='lvl2', channel_interface_list=channel_list)
        level_two_relays.append(new)

    transmit_nodes = []
    for _ in range(ground_nodes - ground_nodes//2):
        new_node = generating_node.ImprovedMultipleChannelNode(time_equivalent, packet_size=1, queue_size=500, transmit_rate=1250, gen_rate=1250,
                                        destinations=receiving_nodes,  type='src', channel_interface_list=channel_list)
        transmit_nodes.append(new_node)

    ''' Create connections '''

    ebunch = [] #list of edge-tuples
    half1 = len(level_one_relays)//2
    for tn in transmit_nodes:
        for rn in level_one_relays[:half1]:
            temp = (tn, rn, {'Weight' : 1, 'Channel': channel_list})
            ebunch.append(temp)

    for dn in receiving_nodes:
        for rn in level_one_relays[half1:]:
            temp = (dn, rn, {'Weight': 1, 'Channel': channel_list})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn2 in level_two_relays:
            temp = (rn1, rn2, {'Weight': 1, 'Channel': channel_list})
            ebunch.append(temp)

    for rn1 in level_one_relays:
        for rn12 in level_one_relays:
            if not rn1 is rn12:
                temp = (rn1, rn2, {'Weight': 1, 'Channel': channel_list})
                ebunch.append(temp)

    network.add_edges_from(ebunch)

    ''' Data Structures'''
    network_data = defaultdict(None)

    '''############### RUN LOOP #################'''
    time_steps = t_steps

    print('Starting network...')
    while time_steps > 0:

        #### RUNNING NETWORK ####
        for node in network.nodes:
            node.generate(network)

            # Transmit to channel
            #TODO: Idea, pass channel name to transmit (looping through available channels)
            node.transmit(channel_list)

        # 'Access' the packets in the channel
        for edge in network.edges:
            n1, n2 = edge
            for_n1 = []
            for_n2 = []
            for chan in network[n1][n2]['Channel']:
                for_n1 += chan.receive_access(n2, n1)
                for_n2 += chan.receive_access(n1, n2)

            n1.receive(for_n1)
            n2.receive(for_n2)

            #Update weights
            network[n1][n2]['Weight'] += (len(for_n1) + len(for_n2))

        print(time_steps)
        #### RUNNING NETWORK ####
        time_steps = time_steps - 1
    '''##########################################'''
    print('Finished')
    # Collect all data from the nodes
    for node in network.nodes():
        network_data[str(node)] = node.metadata

    # network_data[str(main_channel1)] = main_channel1.metadata
    network_data['dropped_count'] = generating_node.Packet.dropped_count
    network_data['arrived_count'] = generating_node.Packet.arrived_count
    generating_node.Packet.reset()
    return network_data

''' DRAW THE NETWORK '''
# net_data = run_network_for(4, 6, 2, 50, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# print('Arrived Packets:', str(net_data['arrived_count']))
sns.set()
data = [[],[]]
g=4;a=6;s=2
for i in range(1,20):
    g=g+2; a=a+2; s=s+2
    net_data = run_multiple_chan_network_for(g, a, s, 30, 0.001)
    print('Dropped Packets:', str(net_data['dropped_count']))
    dp = net_data['dropped_count']
    print('Arrived Packets:', str(net_data['arrived_count']))
    ap = net_data['arrived_count']
    data[0].append((dp*100)/ap)
    data[1].append(4*i + 6*i + 2*i)
fig, ax = plt.subplots()
ax.plot(data[1],data[0], sns.xkcd_rgb["pale red"])

data = [[],[]]
g=4;a=6;s=2
for i in range(1,20):
    g=g+2; a=a+2; s=s+2
    net_data = run_improved_multiple_chan_network_for(g, a, s, 30, 0.001)
    print('Dropped Packets:', str(net_data['dropped_count']))
    dp = net_data['dropped_count']
    print('Arrived Packets:', str(net_data['arrived_count']))
    ap = net_data['arrived_count']
    data[0].append((dp*100)/ap)
    data[1].append(4*i + 6*i + 2*i)

ax.plot(data[1],data[0], sns.xkcd_rgb["denim blue"])

ax.set_xlabel('Number of nodes')
ax.set_ylabel('Packet loss rate (%)')
ax.legend(['Hardcoded', 'Hardcoded-Optimized'])
# net_data = run_multiple_chan_network_for(4, 6, 2, 300, 0.001)



# print('Dropped Packets:', str(net_data['dropped_count']))
# dp = net_data['dropped_count']
# print('Arrived Packets:', str(net_data['arrived_count']))
# ap = net_data['arrived_count']
# data.append((ap/dp)*100)
#
# net_data = run_multiple_chan_network_for(8, 12, 4, 300, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# dp = net_data['dropped_count']
# print('Arrived Packets:', str(net_data['arrived_count']))
# ap = net_data['arrived_count']
# data.append((ap/dp)*100)
#
# net_data = run_multiple_chan_network_for(16, 24, 8, 300, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# dp = net_data['dropped_count']
# print('Arrived Packets:', str(net_data['arrived_count']))
# ap = net_data['arrived_count']
# data.append((ap/dp)*100)

# net_data = run_network_for(6, 8, 2, 100, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# print('Arrived Packets:', str(net_data['arrived_count']))
# net_data = run_network_for(12, 16, 4, 100, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# print('Arrived Packets:', str(net_data['arrived_count']))

# labels = []
# for key in net_data.keys():
#     if 'lvl' in key:
#         ax.plot(net_data[key][2])
#         labels.append(key)
#     if 'Channel' in key:
#         print(net_data[key]['dropped_packets'])
#
# ax.legend(labels)
plt.show()
