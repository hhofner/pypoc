import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import itertools
import seaborn as sns
import pandas as pd
import numpy as np
import itertools
import pickle
import os

import topology
import networkx as nx
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode

verbose = True
verboseprint = print if verbose else lambda *a, **k: None


class PyPocNetwork(nx.Graph):
    def initialize(self, packet_size):
        self.packet_size = packet_size
        self.initialize_step_values()

        self.overall_throughput = 0

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
        
        # time_to_dest = self.tick - packet.born_tick
        # self.overall_throughput = packet.size / (time_to_dest * self.step_value)

        self.overall_throughput = (self.total_byte_count / (self.tick * self.step_value)) * 8

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
            # for edge in self.edges:
            #     print(edge)
            #     input(self[edge[0]][edge[1]]['Channel'])

            self.update_channel_loads()
        print(f'########### FINISH ###########')
        print(f'\tGENERATED PACKETS: {Packet.generated_count}')
        print(f'\tARRIVED PACKETS: {Packet.arrived_count}')
        print(f'\tDROPPED PACKETS: {Packet.dropped_count}')
        print(f'\tPACKET LOSS RATE: {Packet.dropped_count/Packet.generated_count}')
        print(f'\tOVERALL THROUGHPUT: {self.overall_throughput/1e3} KBps')
        for node in self.nodes:
            print(node.get_pretty_data())
        # input('yeah')

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

    # Deprecation
    def can_send_through(self, key, node1, node2, bytes, received_edge=None):
        if key != 'Channel':
            input(f'Warning: Did you really mean {key}?')
        
        v = None
        u = None
        link_found = False
        if not received_edge:
            for edge in self.edges:
                v, u = edge
                if (v is node1 and u is node2) or (v is node2 and u is node1):
                    link_found = True
                    break

            if link_found:
                if self[u][v]['Channel'] + bytes < self[u][v]['Bandwidth']:
                    self[u][v]['Channel'] += bytes
                    verboseprint(f'Creating link reference {node1}->{node2}')
                    return (True, self[u][v])
                else:
                    return (False, self[u][v])
            elif not link_found:
                raise Exception(f'Link not found between {node1} and {node2}')
        
        elif received_edge:
            if received_edge['Channel'] + bytes < received_edge['Bandwidth']:
                received_edge['Channel'] += bytes
                return (True, received_edge)
            else:
                return (False, received_edge)

    # Deprecation
    def reset_bandwidths(self):
        #TODO: Consider, at the end of every tick do we reset the load number
        # on each channel? Given that, what will happen next tick? And does this
        # make sense ?
        for edge in self.edges:
            v, u = edge
            self[v][u]['Channel'] = 0


def run_network(minutes, src_node_count=4, rel_node_count=12):
    network = PyPocNetwork()

    # network.add_edges_from(topology.grid(src_count=src_node_count))
    network.add_edges_from(topology.sagin(src_count=src_node_count))

    network.initialize(packet_size=500)
    network.run_for(minutes)

    return network

def calculate_cont_throughput(network, prev_data=None):
    '''
    Calculate the continuous throughput of a network 
    '''
    pass

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
        net = run_network(5, src_node_count=count, rel_node_count=8)
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
