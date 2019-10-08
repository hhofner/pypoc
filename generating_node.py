from collections import deque,  namedtuple
import networkx as nx
import numpy as np
import random

# Packet = namedtuple('Packet', ['size', 'src', 'dest', 'path'])
class Packet:
    arrived_count = 0
    dropped_count = 0

    @staticmethod
    def dropped():
        Packet.dropped_count += 1

    @staticmethod
    def arrived():
        Packet.arrived_count += 1

    @staticmethod
    def reset():
        Packet.dropped_count = 0
        Packet.arrived_count = 0

    def __init__(self, size, src, dest, path):
        self._size = size
        self._src = src
        self._dest = dest
        self._path = path
        self.now = src

    @property
    def size(self):
        return self._size

    @property
    def src(self):
        return self._src

    @property
    def dest(self):
        return self._dest

    @property
    def path(self):
        return self._path

class Node:
    current_id = 0

    @staticmethod
    def get_id():
        id = Node.current_id
        Node.current_id += 1
        print(f'Instantiating Node {id}')
        return id

    def __init__(self, time_step, packet_size, queue_size, transmit_rate, gen_rate, destinations=None, type=None):
        self.id = Node.get_id()
        if packet_size:
            self.gen_rate = gen_rate * time_step / packet_size
            self.packet_size = packet_size
        else:
            self.gen_rate = 0

        self.transmit_rate = transmit_rate * time_step
        self.queue = deque()
        self.queue_max_size = queue_size
        print(f'Transmit Rate: {self.transmit_rate}')

        self.destinations = destinations
        self.type = type

        self.metadata = [[],[],[], 0] # [[dropped packets], [generated_packets], [transmitted_packets], total_received_packets]

        self.gen_nokori = 0 # This is a "left-over" counter to include the "0.25" packets
        self.transmit_nokori = 0

    def transmit(self):
        '''
        Return a list of packets fetched from the nodes queue
        with a total bit count of more or less the nodes
        transmit rate.

        :return: List of Packet tuples, can be empty
        '''
        packets_to_transmit = []
        if self.transmit_nokori > 0 and self.transmit_nokori < 1:
            self.transmit_nokori += self.transmit_rate
        else:
            self.transmit_nokori = np.random.normal(self.transmit_rate)
        to_send_bit_count = 0
        while(self.transmit_nokori > 1):
            try:
                packet = self.queue.popleft()
            except IndexError as err:
                break
            else:
                to_send_bit_count += packet.size
                packets_to_transmit.append(packet)
            self.transmit_nokori = self.transmit_nokori - 1
        total_size = 0
        for p in packets_to_transmit:
            total_size += p.size
        self.metadata[2].append(total_size)

        return packets_to_transmit

    def receive(self, received_packets):
        '''
        Receive a list of packets and insert them into the
        queue one by one until the total inserted size of bits
        is larger than the max queue size or until the list is
        done.
        :param packets: list of Packet tuples
        :return:
        '''
        dropped_packets = 0
        current_size = self._get_current_queue_size()
        for packet in received_packets:
            if current_size <= self.queue_max_size:
                current_size += packet.size
                self.queue.append(packet)
                self.metadata[3] += 1 # increment received packet count
                if self.type == 'dest':
                    packet.arrived()
            else:
                dropped_packets += 1
                self.metadata[0].append(dropped_packets)

    def generate(self, network):
        '''
        Generate packets and push onto the nodes queue. Uses a passed in
        network object to figure out route for generated packets.

        :param network: A networkx Graph object instance
        :return:
        '''
        if self.gen_rate > 0:
            num_of_generated_packets = 0
            if not self.destinations:
                raise Exception(f'No destinations or '
                                    'network declared for Node {self.id}')
            self.gen_nokori += np.random.normal(self.gen_rate)

            packet_size = self.packet_size
            while (self.gen_nokori > 1):
                src = self
                dest = random.choice(self.destinations)

                path = self._get_string_path(nx.dijkstra_path(network,
                                                src, dest, 'Weight'))

                # print(nx.shortest_path(network, src, dest, 'Weight'))
                # input(f'Path for {src.id} to {dest.id}: {path} from ')

                new_packet = Packet(packet_size, src, dest, path)
                self.queue.append(new_packet)
                num_of_generated_packets += 1
                self.gen_nokori = self.gen_nokori - 1
                if self.gen_nokori < 0:
                    raise Exception('gen_nokori is less than zero')
            self.metadata[1].append(num_of_generated_packets)
        else:
            self.metadata[1].append(0)

    def _get_current_queue_size(self):
        current_size = 0
        for node in self.queue:
            current_size += node.size

        return current_size

    def _get_string_path(self, path):
        return ('-'.join(str(n.id) for n in path))

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        if not self.type:
            return f'Node {self.id}'
        else:
            return f'Node[{self.type}]-{self.id}'

class MultipleChannelNode(Node):
    pass
