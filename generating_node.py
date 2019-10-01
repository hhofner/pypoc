from collections import deque,  namedtuple
import networkx as nx
import numpy as np
import random

Packet = namedtuple('Packet', ['size', 'src', 'dest', 'path'])

class Node:
    current_id = 0

    @staticmethod
    def get_id():
        id = Node.current_id
        Node.current_id += 1
        print(f'Instantiating Node {id}')
        return id

    def __init__(self, time_step, packet_size, queue_size, transmit_rate, gen_rate, destinations=None):
        self.id = Node.get_id()
        self.gen_rate = int(gen_rate * time_step)
        self.transmit_rate = int(transmit_rate * time_step)
        self.packet_size = packet_size
        self.queue = deque()
        self.queue_max_size = queue_size

        self.destinations = destinations

        self.data = [[]] # [[dropped packets]]

    def transmit(self):
        '''
        Return a list of packets fetched from the nodes queue
        with a total bit count of more or less the nodes
        transmit rate.

        :return: List of Packet tuples, can be empty
        '''
        packets_to_transmit = []
        max_bits = np.random.normal(self.transmit_rate)
        to_send_bit_count = 0
        while(to_send_bit_count < max_bits):
            try:
                packet = self.queue.popleft()
            except IndexError as err:
                break
            else:
                to_send_bit_count += packet.size
                packets_to_transmit.append(packet)

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
            else:
                dropped_packets += 1
                self.data[1].append(dropped_packets)

    def generate(self, network):
        if self.gen_rate:
            if not self.destinations or not self.network:
                raise Exception(f'No destinations or network declared for Node {self.id}')
            max_bits_to_send = self.gen_rate

            while (max_bits_to_send > 0):
                size = self.packet_size
                src = self.id
                dest = random.choice(self.destinations)
                path = nx.shortest_path(network, src, dest)
                new_packet = Packet(size, src, dest, path)
                self.queue.append(new_packet)
                max_bits_to_send -= size
        else:
            pass

    def _get_current_queue_size(self):
        current_size = 0
        for node in self.queue:
            current_size += node.size

        return current_size

    def __hash__(self):
        return hash(self.id)


