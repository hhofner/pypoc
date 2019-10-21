'''
nodes.py

This module contains Node objects.

Author: Hans Hofner
'''
import methods
from collections import deque, defaultdict


class SimpleNode:
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
        if self.gen_rate > 0:
            methods.simple_generate(self, network, self.gen_rate)

    def transmit_to(self, channel):
        if self.transmit_rate > 0:
            channel.receive(methods.simple_transmit(self, self.transmit_rate))
        else:
            pass

    def receive(self, received_packets):
        methods.simple_receive(self, received_packets)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        if not self.type:
            return f'Node[{self.id}]'
        else:
            return f'{self.type}[{self.id}]'
