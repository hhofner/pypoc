import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import itertools
import seaborn as sns
import pandas as pd
import numpy as np
import itertools
import pickle
import os

from scipy.spatial import distance
import topology
import signal_tools
import networkx as nx
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode

verbose = True
verboseprint = print if verbose else lambda *a, **k: None

class Infodata:
    def __init__(data, information):
        self._data = data
        self._information = information

class NetworkData:
    def __init__():
        self.throughputs = Infodata([], 
        'List of whole network throughput values per time.')
        self.overall_throughput = Infodata(0, 
        'The overall throughput of the network')
        
class PyPocNetwork(nx.Graph):
    def initialize(self, packet_size):
        self.packet_size = packet_size
        self.initialize_step_values()
        self.overall_throughput = 0

        self.data = {'throughputs':[]}

    def initialize_step_values(self):
        highest_bandwidth = self.find_highest_bandwidth()
        self.step_value = self.packet_size/highest_bandwidth

        for node in self.nodes:
            node.step_value = self.step_value

    def find_highest_bandwidth(self):
        highest = None
        for edge in self.edges:
            v, u = edge
            if highest is None:
               highest = self[u][v]['Bandwidth']
            elif self[u][v]['Bandwidth'] < highest:
                highest = self[u][v]['Bandwidth']
        
        return highest

    def update_throughput(self, packet):
        try:
            self.total_byte_count += packet.size
        except:
            self.total_byte_count = packet.size

        self.overall_throughput = (self.total_byte_count / (self.tick * self.step_value)) * 8
        self.data['throughputs'].append(self.overall_throughput)

    def get(self, key, node1, node2):
        return self[node1][node2][str(key)]
    
    def run_for(self, minutes):
        seconds = minutes * 60
        ticks = seconds / self.step_value
        self.tick = 1
        while self.tick < ticks:
            print(f'\n~~~~ TIME {self.tick} ~~~~\n')
            for node in self.nodes:
                print(f'---->: {node}')
                node.run(self)
            self.tick += 1

            self.update_channel_loads()
            self.update_channel_links()

        print(f'########### FINISH ###########')
        print(f'\tGENERATED PACKETS: {Packet.generated_count}')
        print(f'\tARRIVED PACKETS: {Packet.arrived_count}')
        print(f'\tDROPPED PACKETS: {Packet.dropped_count}')
        print(f'\tPACKET LOSS RATE: {Packet.dropped_count/Packet.generated_count}')
        print(f'\tOVERALL THROUGHPUT: {self.overall_throughput/1e3} KBps')
        self.packet_drop_rate = (Packet.dropped_count / Packet.generated_count) * 100

    def reset(self):
        Packet.reset()

    def get_count_of(self, type_of_node):
        count = 0
        for node in self.nodes:
            if node.type == type_of_node:
                count += 1
        return count

    def update_channel_loads(self):
        for edge in self.edges:
            n1, n2 = edge
            self[n1][n2]['Channel'] = len(n1.queue) + len(n2.queue)

    def update_channel_links(self):
        for node in self.nodes:
            if node.is_moving:
                print(f'Updating links for {node}')
                ''' Find distance between all other nodes'''
                for edge in self.edges(node):
                    n1, n2 = edge
                    dist = distance.euclidean(n1.position, n2.position)
                    # input(f'Distance: {dist}\n\tn1 position: {n1.position}\n\tn2 position: {n2.position}')
                    ''' Then calculate the capacity for that link'''
                    capacity = signal_tools.calculate_cap(dist)/8 # in BYTES
                    # input(f'Calculated Capacity: {capacity}')
                    '''Then Change the capacity'''
                    self[n1][n2]['Bandwidth'] = capacity
                    self.initialize_step_values()

    def run_network(minutes, structure, bandwidth, src_node_count, relay_node_count, 
                    dest_node_count, packet_size):
        self.add_edges_from(structure(src_node_count, relay_node_count, dest_node_count))
        self.initialize(packet_size)
        self.run_for(minutes)

if __name__ == '__main__':
    # net = run_network(1)  # TODO: Currently at limited transmission

    # print(f'\tGenerated Packets: {Packet.generated_count}')
    # print(f'\ttArrived Packets: {Packet.arrived_count}')

    # print(f'\t{"#"*10}Individual Node Data{"#"*10}')
    # for n in net.nodes:
    #     print(n.get_pretty_data())

    ## Plotting ##
    # fig, ax = plt.subplots()

    sns.set()
    sns.set_style('whitegrid')
    # sns.set_context('poster')
    fig, (ax1, ax2, ax3) = plt.subplots(3,1)
    palette = itertools.cycle(sns.color_palette())

    # patches = []
    # for n in net.nodes:
    #     if n.type == 1:
    #         now_color = next(palette)
    #         queue_lengths = n.data['queue_size']
    #         plt.plot(queue_lengths, color=now_color)
    #         patches.append(mpatches.Patch(color=now_color, label=n))
    # plt.legend(handles=patches)

    ## Throughput Plotting ##
    simple_network = None
    complex_network = None
    throughputs = []
    packet_loss_rates = []
    packet_avg_delays = []
    for count in range(4, 43):
        net = run_network(5, structure=topology.grid, src_node_count=count)
        if simple_network is None:
            simple_network = net
        if count == 30:
            complex_network = net
        packet_loss_rates.append((Packet.dropped_count / Packet.generated_count) * 100)
        packet_delays = []
        for node in net.nodes:
            if node.type == 2:
                for packet in node.queue:
                    packet_delays.append(packet.delay)
        packet_avg_delays.append(sum(packet_delays)/len(packet_delays) * net.step_value)

        throughputs.append(net.overall_throughput/1e3)
        Packet.reset()
    
    files_to_compare = ['thruput', 'packet_delay', 'packet_loss']

    ## Axes 1 ##
    # ax1.plot([i for i in range(1,40)], throughputs, marker='o')
    ax1.plot(throughputs, marker='o')
    ax1.set_title('Throughput Performance: 1Kbps Generation Rate w/ increasing source nodes')
    # ax1.set_xlabel('Number of SRC Nodes')
    ax1.set_ylabel('Kbps')
    # if os.path.isfile(files_to_compare[0]):
    #     with open(files_to_compare[0], 'rb') as fp1:
    #         prev_thruput = pickle.load(fp1)
    #         ax1.plot(prev_thruput, color='grey', marker='*')
    # Save current
    with open(f'throughput_', 'wb') as tp:
        pickle.dump(throughputs, tp)

    ## Axes 3 (!!) ##
    # pos_dict = {}
    # X,Y = np.mgrid[1:5:1, 1:5:1]
    # Z = list(zip(X.flatten(), Y.flatten()))
    # for n in simple_network.nodes:
    #     id = n.id
    #     pos_dict[n] = Z[id]
    # nx.draw_networkx(simple_network, ax=ax3, pos=topology.get_sagin_positional(simple_network))
    # nx.draw_networkx(simple_network, ax=ax3, pos=pos_dict)
    # ax3.set(title='Example Grid Topology: 8Kbps Bandwidth')
    # ax3.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, labelleft=False)
    # plt.table(cellText=[['8 Kbps', '1 KBytes']], rowLabels=['Global Params'], colLabels=['Bandwidth', 'Max Buffer Size'], loc='bottom')
    ax3.plot(packet_loss_rates, marker='x', color='red')
    ax3.set_title('Packet loss rate for increasing source nodes')
    ax3.set_ylabel('Percentage')

    ## Axes 2 ##
    # for n in complex_network.nodes:
    #     if n.type == 1:
    #         ax2.plot(n.data['queue_size'], label=f'{n}')
    # ax2.legend(loc='upper left')
    # ax2.set_title(f'Buffer sizes for network with {complex_network.get_count_of(0)} source nodes per time')
    # # ax2.set_xlabel('Time')
    # ax2.set_ylabel('Number of packets')
    ax2.plot(packet_avg_delays, color='green', marker='*')
    ax2.set_title('Average Package Delay')

    # # Plot previous
    # with open('packet_delay', 'rb') as fp:
    #     prev_packet_delay = pickle.load(fp)
    #     ax2.plot(prev_packet_delay, color='grey', marker='*')
    # Save current
    with open('packet_delay', 'wb') as tp:
        pickle.dump(packet_avg_delays, tp)

    plt.show()
