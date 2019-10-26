from collections import deque
import matplotlib.pyplot as plt
import random

import networkx as nx


class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

    def __init__(self, path, size=1):
        '''
        Increments the Packet class-wide generated_count variable and
        assigns object attributes.

        :param path: List of Node objects representing a path from src to dest.
        :param size: Integer representing an arbitrary size of the Packet.
        '''
        self.size: int = size

        self._has_arrived = False
        self._has_dropped = False
        self.id = Packet.generated_count
        Packet.generated_count += 1

        self.path_nodes = {'past': [], 'future': []}
        self.path_nodes['past'].append(path[0])
        self.path_nodes['future'].extend(path[1:])

    def check_and_update_path(self, arrived_node):
        '''
        Check if the Node that received `this` packet aligns with
        the path, and if so, update. If path empty, it means it
        arrived at destination node.

        :param arrived_node: Node object
        '''
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

    def __str__(self):
        return f'Packet {self.id}'

    def __repr__(sef):
        return f'Packet(ID:{self.id}, SIZE:{self.size}, PATH{self.path})'


class Node:
    count = 0

    def __init__(self, type):
        '''
        Increment Node class `count` attribute and assign it to
        Node instance id attribute. Create data element.

        :param type: Integer corresponding to predefined integer types,
            i.e. Source node, Relay node or Destination node.
        '''
        self.id = Node.count
        Node.count += 1

        self.dest_node_list = []
        self.queue = deque()

        self.type = type

        self.initalize_data()

    def transmit(self, network):
        '''
        Create Packet instance and send it to the next
        Node destination based on the path.

        :param network: Networkx Graph instance that has all info on network.
        '''
        if not self.dest_node_list:
            self.update_dest_node_list(network)
        dest = random.choice(self.dest_node_list)
        path = nx.shortest_path(network, self, dest)
        packet = Packet(path)

        self.data['transmited_packets'].append(packet)
        packet.next_node.receive(packet)

    def relay(self, network):
        '''
        Relay one packet from queue onto the next node.

        :param network: Networkx Graph instance that has all info on network.
        '''
        if self.queue:
            popped_packet = self.queue.popleft()
            popped_packet.next_node.receive(popped_packet)

            self.data['relayed_packets'].append(popped_packet)

    def receive(self, received_packet):
        '''
        Update packet path and append to node queue.
        '''
        received_packet.check_and_update_path(self)
        self.queue.append(received_packet)

    def run(self, network):
        '''
        '''
        if self.type == 0:
            self.transmit(network)
        elif self.type == 1:
            self.relay(network)

    def update_dest_node_list(self, network, dest_ids=None):
        if not dest_ids:
            for node in network.nodes:
                if node.type == 2:
                    self.dest_node_list.append(node)

    def initalize_data(self):
        '''
        Initialize data structure for node.
        '''
        self.data = {'queue_size': [len(self.queue)],
                     'transmited_packets': [],
                     'relayed_packets': [],
                     'received_packets': [],
                     }

    def get_pretty_data(self):
        '''
        Create a pretty string representation of the nodes
        data.

        :return pretty_data: String representing the data, for printing.
        '''
        pretty_data = f'Node {self.id}'
        for key in self.data.keys():
            pretty_data += f'\n\t{key}\n\t\t'
            length = len(self.data[key])
            pretty_data += f'length: {length}'

        return pretty_data

    def __hash__(self):
        return self.id

    def __repr__(self):
        return f'(id:{self.id},t:{self.type})'
