from collections import deque
import random

import networkx as nx


class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

    def __init__(self, path, size=1):
        '''
        '''
        self.size: int = size

        self._has_arrived = False
        self._has_dropped = False
        Packet.generated_count += 1

        self.path_nodes = {'past': [], 'future': []}  # ID's of nodes
        self.path_nodes['past'].append(path[0])
        self.path_nodes['future'].extend(path[1:])

    def check_and_update_path(self, arrived_node):
        if arrived_node is self.path_nodes['future'][0]:
            arrived_node = self.path_nodes['future'][0]
            self.path_nodes['past'].append(arrived_node)
            self.path_nodes['future'].remove(arrived_node)
        else:
            raise Exception(f'Next node in path does not match! '
                            f'{arrived_node} =/= '
                            f'{self.path_nodes["future"][0]}')

        # If empty no more future
        if not self.path_nodes['future']:
            self.arrived()

    def arrived(self):
        if not self._has_arrived:
            Packet.arrived_count += 1
        self._has_arrived = True

    def dropped(self):
        if not self._has_dropped:
            Packet.dropped_count += 1
        self._has_dropped = True

    @property
    def next_node(self):
        return self.path_nodes['future'][0]


class Node:
    count = 0

    def __init__(self, type):
        self.id = Node.count
        Node.count += 1

        self.dest_node_list = []
        self.queue = deque()

        self.type = type

    def transmit(self, network):
        '''
        Send packet(s) to a random destination.
        '''
        if not self.dest_node_list:
            self.update_dest_node_list(network)
        dest = random.choice(self.dest_node_list)
        path = nx.shortest_path(network, self, dest)
        packet = Packet(path)
        packet.next_node.receive(packet)

    def relay(self, network):
        '''
        Relay one packet from queue onto the next node.
        '''
        if self.queue:
            popped_packet = self.queue.popleft()
            popped_packet.next_node.receive(popped_packet)

    def receive(self, received_packet):
        '''
        Update packet path and append to node queue.
        '''
        received_packet.check_and_update_path(self)
        self.queue.append(received_packet)

    def run(self, network):
        if self.type == 0:
            self.transmit(network)
        elif self.type == 1:
            self.relay(network)

    def update_dest_node_list(self, network, dest_ids=None):
        if not dest_ids:
            for node in network.nodes:
                if node.type == 2:
                    self.dest_node_list.append(node)

    def __hash__(self):
        return self.id

    def __repr__(self):
        return f'(id:{self.id},t:{self.type})'
