import networkx as nx
import simple_node
import numpy as np
import topology_schemes
from collections import defaultdict
import logging

class Network(object):
    '''
    Main class responsible for creating and running a simulation instance of a network, as well as
    handling the logic for outbound packets (packets being transmitted).

    The network object expects an 'environment time' argument when being initialized. This parameter indicates how
    many time steps the network will run for.
    '''
    def __init__(self, env_time):
        self.env_time: int = env_time
        self.nodes = []
        self.network = nx.Graph()
        self.outbound_packets = []
        self.channel_capacity = 0 #TODO: Figure out usage

        ### Data Collection Features ###
        # #TODO: Figure out a better solution

        # ndarray to keep values of all node weights at each time point
        self.weight_matrix = None

        # Dictionary that keeps the queue values
        self.node_values = defaultdict(list)

        # Dictionary that keeps dropped packet values
        self.dropped_packets = defaultdict(list)

        # Dictionary to contain the number of transmitted packets per time point
        self.packet_transmit_count = defaultdict(int)

    def set_up_network_with(self):
        '''

        :return: None
        '''
        ebunch, temp_nodes = topology_schemes.default_sagin()

        self.nodes += temp_nodes
        self.network.add_edges_from(ebunch)

        #Initialize Weight Matrix
        self.weight_matrix = np.ones((self.env_time, len(self.nodes), len(self.nodes)))

    def run(self):
        if not self.nodes:
            raise Exception(f'Error: Network is empty! Please set up the network by calling the method set_up().')
        else:
            while self.env_time > 0:

                self.evaluate_transmission()
                self.transmit_packages_from_nodes()

                self.collect_data()

                self.env_time -= 1

    def transmit_packages_from_nodes(self):
        for n in self.nodes:
            possible_packets = n.transmit()
            if possible_packets:
                self.outbound_packets += possible_packets
                self.packet_transmit_count[self.env_time] += len(possible_packets)

            # Important, how to keep safe?
            n.time += 1

    def evaluate_transmission(self):
        # Evaluate packet destinations and overwrite their paths at every point
        for _ in range(len(self.outbound_packets)):
            outbound_packet = self.outbound_packets.pop() # Should this be a queue?
            # new_path = nx.dijkstra_path(self.network, outbound_packet.source, outbound_packet.destination, weight='Weight')
            # outbound_packet.path = new_path if not outbound_packet.path else outbound_packet.path
            outbound_packet.set_path(self.network)

            next_node = outbound_packet.next_hop()
            self.nodes[next_node].receive(outbound_packet) #Sketchy TODO: Better solution

            # At every env_time point, update amount of packets being sent through
            # edge path[0], path[1]
            self.weight_matrix[self.env_time-1][outbound_packet.source][outbound_packet.next_hop()] += 10
            self.weight_matrix[self.env_time-1][outbound_packet.next_hop()][outbound_packet.source] += 1

        # Update edge values according to the number of packets
        # being sent through that edge at the previous time
        # TODO: Create a better way to implement edge value changes
        for edge in self.network.edges:
            u, v = edge
            try:
                self.network.edges[u,v]['Weight'] = self.weight_matrix[self.env_time - 1][u][v]
            except Exception as err:
                raise

    def collect_data(self):
        for n in self.nodes:
            self.node_values[n.id].append(len(n.queue))
            self.dropped_packets[n.id].append(len(n.dropped_packets))

if __name__ == '__main__':
    pass