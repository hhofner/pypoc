from collections import deque, defaultdict
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import numpy as np
import math
import random
import itertools

import networkx as nx

verbose = True
verboseprint = print if verbose else lambda *a, **k: None


class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

    @staticmethod
    def reset():
        Packet.arrived_count = 0
        Packet.dropped_count = 0
        Packet.generated_count = 0


    def __init__(self, path, tick_time, size=1):
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

        # The `tick` at which the packet object was instanitated
        self.born_tick = tick_time
        self.died_tick = None

    def check_and_update_path(self, arrived_node, tick):
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
            self.arrived(tick)

    def arrived(self, tick):
        if not self._has_arrived:
            Packet.arrived_count += 1
            print(f'{self} arrived!')
            self.died_tick = tick
            self.delay = self.died_tick - self.born_tick
        self._has_arrived = True
        # Update average delay

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

    def __init__(self, type, step_value):
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
        self.queue = deque()

        self.type = type
        self.time = 0
        self.packet_size = 1
        self.step_value = step_value

        self.edges = defaultdict(lambda: None)

        self.initalize_data()

    @abstractmethod
    def transmit(self, network):
        pass

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
            popped_packet.next_node.receive(network, popped_packet)
            self.data['relayed_packets'].append(popped_packet)

    def receive(self, network, received_packet):
        '''
        Update packet path and append to node queue.
        '''
        verboseprint(f'{self} received {received_packet}')
        received_packet.check_and_update_path(self, network.tick)
        self.wait_queue.append(received_packet)
        if self.type == 2:
            network.update_throughput(received_packet)
        self.data['received_packets'].append(received_packet)

    def run(self, network):
        '''
        '''
        if self.type == 0:
            print(f'{self} transmitting.')
            self.transmit(network)
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
        
        if len(self.dest_node_list) == 0:
            raise Exception(f'No destinations registered for node {self}')

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

    def get_queue_size(self):
        total = 0 # in bytes
        for packet in self.queue:
            total += packet.size
        return total

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

    def create_packet(self, network, next_hop=None):
        if not self.dest_node_list:
            self.update_dest_node_list(network)
        dest = random.choice(self.dest_node_list)
        if next_hop is None:
            path = nx.shortest_path(network, self, dest, weight='Channel')
        else:
            path = nx.shortest_path(network, next_hop, dest, weight='Channel')
            path = [self] + path

        # TODO: Implement the functionality of nodes that can't reach
        # the destination from next_hop -- for now assume they can
        return Packet(path, network.tick, size=self.packet_size)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return (self.__class__ == other.__class__
               and self.id == other.id)

    def  __str__(self):
        if self.type == 0:
            t = 'src'
        elif self.type == 1:
            t = 'rel'
        elif self.type == 2:
            t = 'dest'
        return f'Node {self.id} [{t}]'

    def __repr__(self):
        return f'(Node id:{self.id},t:{self.type})'


class MovingNode(Node):
    def __init__(self, type, step_value, mobility_model):
        super().__init__(type, step_value)
        self.position = (0, 0, 0)  #x, y, z
        self.mobility_model = mobility_model
        self.is_moving = True if mobility_model else False

    def initalize_data(self):
        super().initalize_data()
        self.data.update({'position_list': []})

    def update_data(self):
        super().update_data()
        self.data['position_list'].append(self.position)

    def run(self, network):
        if self.type == 0:
            print(f'{self} transmitting.')
            self.transmit(network)
        elif self.type == 1:
            print(f'{self} relaying.')
            self.relay(network)

        self.move(network)
        self.update_queue()
        self.update_data()
        
        self.time += 1

    def move(self, network):
        try:
            x, y, z = self.mobility_model(network, self.step_value, self.position)
        except:
            verboseprint(f'Warning: {self} did not move.')
        else:
            self.position = (x, y, z)


class VaryingTransmitNode(MovingNode):
    def __init__(self, type, step_value, mobility_model, packet_size, gen_rate):
        super().__init__(type, step_value, mobility_model)
        self.neighbor_wait_time = {}  # Counter for every neighor when the next step to transmit is
        self.neighbors = {}  # Neighbors and the corresponding bandwidths
        
        self.neighbor = None
        self.transmit_counter = None
        self.gen_step = None  # The time it takes to transmit next

        self.packet_size = packet_size
        self.gen_rate = gen_rate

    def transmit(self, network):
        # Intialize neighbors
        if len(self.neighbors) == 0:
            self.update_neighbor_counter(network)

        # First loop ever
        if self.transmit_counter is None:
            # packet = self.create_packet(network, next(self.neighbor))
            packet = self.create_packet(network)
            packet.next_node.receive(network, packet)
            self.data['transmited_packets'].append(packet)
            
            self.transmit_counter = self.gen_step

        elif self.transmit_counter > 1:
            for _ in range(int(self.transmit_counter)):
                # packet = self.create_packet(network, next(self.neighbor))
                packet = self.create_packet(network)
                packet.next_node.receive(network, packet)
                self.data['transmited_packets'].append(packet)
                self.transmit_counter -= 1
                print('Transmitted')
            
            self.transmit_counter += self.gen_step
        else:
            self.transmit_counter += max(np.random.normal(self.gen_step), self.gen_step)
            # self.transmit_counter += self.gen_step

    def update_neighbor_counter(self, network):
        for neighbor in nx.neighbors(network, self):
            channel_bandwidth = network[self][neighbor]['Bandwidth']
            self.neighbor_wait_time[neighbor] = 0
            self.neighbors[neighbor] = self.packet_size / channel_bandwidth
        
        self.neighbor = (n for n in itertools.cycle(self.neighbors.keys()))
        self.gen_step = (self.gen_rate/self.packet_size) * self.step_value


class VaryingRelayNode(VaryingTransmitNode):
    def relay(self, network):
        if len(self.queue) > 0:
            packet = self.queue.pop()
            packet.next_node.receive(network, packet)


class RestrictedNode(VaryingRelayNode):
    '''
    Node object that has `restrictions` imposed onto it, such as max buffer size.
    '''
    def __init__(self, type, step_value, mobility_model, packet_size, gen_rate, max_buffer_size):
        '''
        :param max_buffer_size: Maximum number of Bytes (!) allowed in device buffer (queue).
        '''
        super().__init__(type, step_value, mobility_model, packet_size, gen_rate)
        self.max_buffer_size = max_buffer_size
    
    def initalize_data(self):
        super().initalize_data()
        self.data.update({'dropped_packets': []})

    def update_queue(self):
        current_queue_size = self.get_queue_size()
        while (current_queue_size < self.max_buffer_size):
            if len(self.wait_queue) <= 0:
                break
            packet = self.wait_queue.pop()
            current_queue_size += packet.size
            self.queue.append(packet)
        
        if len(self.wait_queue) > 0:
            for packet in self.wait_queue:
                packet.dropped()
            self.data['dropped_packets'].append(packet)
            self.wait_queue.clear()