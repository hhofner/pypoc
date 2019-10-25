'''
nodes.py

This module contains Node objects.

Author: Hans Hofner
'''
import methods
from collections import deque, defaultdict


class SimpleNode:
    src_counter = 0
    current_id = 0

    @staticmethod
    def get_id():
        id = SimpleNode.current_id
        SimpleNode.current_id += 1
        print(f'Instantiating Node {id}')
        return id

    def __init__(self, transmit_rate, gen_rate, q_max, dest=None, type=None):
        self.id = SimpleNode.get_id()

        self.transmit_rate = transmit_rate
        self.gen_rate = gen_rate
        self.queue = deque()
        self.max_queue_size = q_max

        self.destinations = dest
        self.type = type

        self.data = defaultdict(int)
        self.data.update({'drop_packet_list': [],
                          'receive_packet_list': [],
                          'generate_packet_list': [],
                          'sent_packet_list': [],
                          'receive_count': 0,
                          'sent_count': 0,
                          'drop_count': 0})

    def generate(self, network):
        if SimpleNode.src_counter > 5:
            if self.type == 'src':
                return
        if self.type == 'src':
            SimpleNode.src_counter += 1
        if self.gen_rate > 0:
            methods.simple_generate(self, network, self.gen_rate)

    def transmit_to(self, channel):
        if self.transmit_rate > 0 and self.queue:
            # Get the destination node (to fetch appropriate packets)
            next_node_id = channel.get_other_node_id(self.id)
            these_packets = methods.simple_transmit(self, self.transmit_rate, next_node_id)
            returned_packets = channel.receive(these_packets)
            print(f'{self} transmitted {these_packets}')
            if returned_packets:
                self.queue.extend(returned_packets)

    def receive(self, received_packets):
        methods.simple_receive(self, received_packets)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        if not self.type:
            return f'Node[ID:{self.id}]'
        else:
            return f'{self.type}[ID:{self.id}]'

class Node:
    count =  0
    def __init__(self):
        self.id = Node.count
        Node.count += 1

        self.queue = deque()

    def send(self):
        pass



class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

    def __init__(self, size):
        self.size = size

        self._has_arrived = False
        self._has_dropped = False
        Packet.generated_count += 1

    def arrived(self):
        if not self._has_arrived:
            Packet.arrived_count += 1
        self._has_arrived = True

    def dropped(self):
        if not  self._has_dropped:
            Packet.dropped_count += 1
        self._has_dropped = True