from collections import deque, defaultdict
import matplotlib.pyplot as plt
import numpy as np
import math
import random

import networkx as nx

verbose = True
verboseprint = print if verbose else lambda *a, **k: None


class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

    def reset():
        Packet.arrived_count = 0
        Packet.dropped_count = 0
        Packet.generated_count = 0

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
            print('Arrived!')
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

    def __repr__(self):
        return f'Packet(ID:{self.id}, SIZE:{self.size})'


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
        self.wait_queue = []
        self.queue = []

        self.type = type
        self.time = 0
        self.packet_size = 1

        self.edges = defaultdict(lambda: None)

        self.initalize_data()

    def transmit(self, network):
        '''
        Create Packet instance and send it to the next
        Node destination based on the path.

        Node (self) will ask the passed in network object if it can send
        the generated packet. At the same time, the Node (self) will try
        and save an `edge` reference for the next node, so for when it is
        used again it doesn't require the network object to iterate over all
        edges in the network.

        :param network: Networkx Graph instance that has all info on network.
        '''
        packet = self.create_packet(network)

        self._transmit(packet, network)

    def _transmit(self, packet, network):
        # `can_send_through()` returns Tuple, (Bool, edge)
        can_send, edge = network.can_send_through('Channel', 
                                                  self,
                                                  packet.next_node,
                                                  packet.size,
                                                  self.edges[packet.next_node])
        if can_send:
            self.data['transmited_packets'].append(packet)
            self.edges[packet.next_node] = edge
            verboseprint(f'{self} Sending {packet} to {packet.next_node}')
            packet.next_node.receive(packet)
        else:
            self.edges[packet.next_node] = edge
            print(f'Can not sent data for Node {self.id}->Node {packet.next_node}')
            self.queue.append

    def transmit_limited(self, network, count):
        '''
        Transmit a limited number of times, based on the passed
        count variable.

        :param count: number of packets to transmit
        '''
        try:
            now_count = self.transmitting_count
        except:
            self.transmitting_count = 0
            now_count = self.transmitting_count
        
        if now_count < count:
            self.transmit(network)
            self.transmitting_count += 1

    def relay(self, network):
        '''
        Relay one packet from queue onto the next node.

        :param network: Networkx Graph instance that has all info on network.
        '''
        to_relay_packets = []
        for packet in self.queue:
            can_send, edge = network.can_send_through('Channel', 
                                                      self, 
                                                      packet.next_node, 
                                                      packet.size, 
                                                      self.edges[packet.next_node])
            if can_send:
                to_relay_packets.append(packet)
                self.edges[packet.next_node] = edge
            else:
                self.edges[packet.next_node] = edge
        
        for p in to_relay_packets:
            popped_packet = self.queue.pop(self.queue.index(p))
            popped_packet.next_node.receive(popped_packet)
            self.data['relayed_packets'].append(popped_packet)

    def receive(self, received_packet):
        '''
        Update packet path and append to node queue.
        '''
        verboseprint(f'{self} received {received_packet}')
        received_packet.check_and_update_path(self)
        self.wait_queue.append(received_packet)

    def run(self, network):
        '''
        '''
        if self.type == 0:
            print(f'{self} transmitting.')
            self.transmit_limited(network, 10)
        elif self.type == 1:
            print(f'{self} relaying.')
            self.relay(network)

        self.update_queue()
        self.update_data()
        
        self.time += 1

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

    def update_data(self):
        self.data['queue_size'].append(len(self.queue))

    def update_queue(self):
        '''
        Push all the packets in wait_queue onto the main
        queue. This is done to give time for packets to propagate
        at every tick, instead of having the packet flow to its 
        destination in one tick.
        '''
        self.queue.extend(self.wait_queue)
        self.wait_queue.clear()

    def get_pretty_data(self):
        '''
        Create a pretty string representation of the nodes
        data.

        :return pretty_data: String representing the data, for printing.
        '''
        pretty_data = f'Node {self.id}'
        for key in self.data.keys():
            if key == 'queue_size':
                pretty_data += f'\n\t{key}\n\t\t'
                length = self.data[key][-1]
                pretty_data += f'length: {length}'
            else:
                pretty_data += f'\n\t{key}\n\t\t'
                length = len(self.data[key])
                pretty_data += f'length: {length}'

        return pretty_data

    def create_packet(self, network):
        if not self.dest_node_list:
            self.update_dest_node_list(network)
        dest = random.choice(self.dest_node_list)
        path = nx.shortest_path(network, self, dest, weight='Channel')
        return Packet(path, size=self.packet_size)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return (self.__class__ == other.__class__
               and self.id == other.id)

    def  __str__(self):
        return f'Node {self.id}'

    def __repr__(self):
        return f'(Node id:{self.id},t:{self.type})'


class MovingNode(Node):
    def __init__(self, type):
        super().__init__(type)
        self.x = 0
        self.y = 0
        self.z = 0

    def initalize_data(self):
        super().initalize_data()
        self.data.update({'position': []})


class VaryingTransmitNode(MovingNode):
    def __init__(self, type, time_conversion, transmit_rate, packet_size):
        super().__init__(type)
        self.time_conversion = time_conversion
        self.transmit_rate = transmit_rate
        self.packet_size = packet_size

        self.generated_queue = []  # list of generated packets to be sent
        self.transmit_step_count = None  # number of transmissions to be made

    def transmit(self, network):
        '''
        '''
        if self.transmit_rate < self.packet_size:
            raise Exception(f'Packet Size can not be larger than Transmit Rate {self.packet_size} > {self.transmit_rate}')

        # First block creates data to be sent. A 10 MByte data will be split into 100 packets, 
        # if packet size is 100KByte. 
        if self.transmit_step_count is None:
            number_of_packet = int(self.transmit_rate / self.packet_size)
            for _ in range(number_of_packet):
                self.generated_queue.append(self.create_packet(network))
            self.transmit_step_count = int(1 / self.time_conversion)  # expecting an integer value like 100, 10, etc
        else:  # Second block sends as many packets as needed per time step.
            to_send_count = int((self.transmit_rate * self.time_conversion) / self.packet_size)
            for _ in range(to_send_count):
                packet = self.generated_queue.pop()
                self._transmit(packet, network)
            self.transmit_step_count -= 1
            if self.transmit_step_count == 0:
                self.transmit_step_count = None

class VaryingRelayNode(MovingNode):
    def __init__(self, type, time_conversion, relay_rate):
        super().__init__(type)
        self.relay_rate = relay_rate * time_conversion
    
    def relay(self, network):
        for _ in range(math.floor(self.relay_rate)):
            super().relay(network)