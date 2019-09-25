import networkx as nx
import numpy as np
import channel
from collections import defaultdict
from math import log2

class Network(object):
    '''
    Main class responsible for creating and running a simulation instance of a network, as well as
    handling the logic for outbound packets (packets being transmitted).

    The network object expects an 'environment time' argument when being initialized. This parameter indicates how
    many time steps the network will run for.
    '''
    def __init__(self, env_time, tse=0.0001):
        self.env_time: int = env_time
        self._time_step_equivalent: int = tse
        self.nodes = []
        self.network = nx.Graph()
        self.outbound_packets = []
        self.channel = None

        self._bandwidth = None
        self._sinr = None
        self._channel_capacity = None

        ######### Data Collection Features #########
        ############################################
        # #TODO: Figure out a better solution: Pandas DF

        # ndarray to keep values of all vertice weights at each time point
        self.weight_matrix = None

        # Dictionary that keeps the queue values per time
        self.node_values = defaultdict(list)

        # Dictionary that keeps dropped packet values
        self.dropped_packets = defaultdict(list)

        # Dictionary to contain the number of transmitted packets per time point
        self.packet_transmit_count = defaultdict(int)

    def set_up_network_with(self, topology_scheme):
        '''

        :return: None
        '''
        ebunch, temp_nodes = topology_scheme()

        self.nodes += temp_nodes
        self.network.add_edges_from(ebunch)
        self._set_topology_for(self.nodes)

        if not self._bandwidth or not self._sinr:
            raise Exception(f'Bandwidth or SINR is not set for Network {self}')
        else:
            self.channel = channel.Channel(self._bandwidth, self._sinr, self._time_step_equivalent)

        #Initialize Weight Matrix
        self.weight_matrix = np.ones((self.env_time, len(self.nodes), len(self.nodes)))

    def run(self):
        if not self.nodes:
            raise Exception(f'Error: Network is empty! Please set up the network by calling the method set_up().')
        else:
            while self.env_time > 0:

                self.evaluate_transmission()
                self.transmit_packets_from_nodes()
                self.collect_data()
                self.env_time -= 1

    def transmit_packets_from_nodes(self):
        for n in self.nodes:
            possible_packets = n.transmit()
            if possible_packets:
                self.channel.access(possible_packets)
                self.packet_transmit_count[self.env_time] += len(possible_packets)

            # Important, how to keep safe?
            n.time += 1

    def evaluate_transmission(self):
        for outbound_packet in self.channel.outbound_packets:
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

    def _set_topology_for(self, nodes):
        for node in self.nodes:
            node.topology = self.network


if __name__ == '__main__':
    pass