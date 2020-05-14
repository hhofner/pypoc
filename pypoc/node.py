'''
Defines the core Node and Packet classes.
'''

__author__ = 'Hans Hofner'

from collections import deque, defaultdict
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import numpy as np
import math
import random
import itertools
import logging

import networkx as nx

logging.basicConfig(level=logging.DEBUG)


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
            # print(f'{self} arrived!')
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
        return f'packet_{self.id}'

    def __repr__(self):
        return f'Packet(ID:{self.id}, SIZE:{self.size})'


class Node:
    count = 0

    def __init__(self, node_type, step_value):
        '''
        Increment Node class `count` attribute and assign it to
        Node instance id attribute. Create data element.

        :param type: Integer corresponding to predefined integer types,
            i.e. Source node, Relay node or Destination node.
        :param step_value:
        '''
        self.id = Node.count
        Node.count += 1

        self.dest_node_list = []
        self.wait_queue = []
        self.queue = deque()

        if not isinstance(node_type, int):
            raise TypeError(f'Invalid type for Node.node_type {self.node_type}')
        self.node_type = node_type
        self.time = 1
        self.packet_size = 1
        self.step_value = step_value

        self.edges = defaultdict(lambda: None)

        self.initalize_data()

    @abstractmethod
    def transmit(self, network):
        pass

    @abstractmethod
    def relay(self, network):
        pass

    def receive(self, network, received_packet):
        '''
        Update packet path and append to node queue.
        '''
        # print(f'{self} received {received_packet}')
        received_packet.check_and_update_path(self, network.tick)
        self.wait_queue.append(received_packet)
        if self.node_type == 2:
            network.update_byte_count(received_packet)
        self.data['received_packets'].append(received_packet)

    def run(self, network):
        '''
        '''
        if self.node_type == 0:
            self.transmit(network)
        elif self.node_type == 1:
            self.relay(network)

        self.update_queue()
        self.update_data()

    @abstractmethod
    def reset_values(self, network):
        pass

    def update_dest_node_list(self, network, dest_ids=None):
        if not dest_ids:
            for node in network.nodes:
                if node.node_type == 2:
                    self.dest_node_list.append(node)

        if len(self.dest_node_list) == 0:
            raise Exception(f'No destinations registered for node {self}')

    def initalize_data(self):
        '''
        Initialize data structure for node.
        '''
        self.data = {'queue_size': [len(self.queue)],
                     'transmitted_packets': [],
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
            try:
                path = nx.shortest_path(network, self, dest, weight='Channel')
            except nx.exception.NetworkXNoPath:
                # print(f'No path {self} -> {dest} ')
                return
        else:
            # TODO: This is dangerous because next_hop might not exist.
            try:
                path = nx.shortest_path(network, next_hop, dest, weight='Channel')
                path = [self] + path
            except nx.exception.NetworkXNoPath:
                print(f'No path {self} -> {dest} ')
                return

        # TODO: Implement the functionality of nodes that can't reach
        # the destination from next_hop -- for now assume they can
        return Packet(path, network.tick, size=self.packet_size)

    def set_name(self, name_of_node):
        self.name = name_of_node

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return (self.__class__ == other.__class__
               and self.id == other.id)

    def  __str__(self):
        if self.node_type == 0:
            t = 'src'
        elif self.node_type == 1:
            t = 'rel'
        elif self.node_type == 2:
            t = 'dest'
        return f'node_{self.id}_{t}_{self.name}'

    def __repr__(self):
        return f'(Node id:{self.id},t:{self.node_type})'


class MovingNode(Node):
    def __init__(self, node_type, step_value, mobility_model):
        '''
        Defines methods and info on moving nodes. Specifically, it uses
        a inputted mobility model generator function to calculate the
        nodes' position in meters.

        :param mobility_model: generator that calculates the next (x, y, z)
                                position of node.
        '''
        super().__init__(node_type, step_value)
        self.position = (0, 0, 0)  #x, y, z  METERS
        self.mobility_model = mobility_model
        self.is_moving = False
        self.is_mobility_object_set = False

    def initalize_data(self):
        super().initalize_data()
        self.data.update({'position_list': []})

    def update_data(self):
        super().update_data()
        self.data['position_list'].append(self.position)

    def run(self, network):
        if self.node_type == 0:
            self.transmit(network)
        elif self.node_type == 1:
            self.relay(network)

        self.move(network)
        self.update_queue()
        self.update_data()

    def move(self, network):
        if not self.is_mobility_object_set:
            self._update_mobility_object(network)
        if self.is_moving:
            try:
                x, y, z = self.mobility_object.get_next_position()
            except:
                raise
            else:
                self.position = (x, y, z)

    def _update_mobility_object(self, network):
        try:
            self.mobility_object = self.mobility_model(network,self)
        except TypeError:
            self.is_mobility_object_set = True
            self.is_moving = False
        else:
            self.is_mobility_object_set = True
            self.is_moving = True


class VaryingTransmitNode(MovingNode):
    def __init__(self, node_type, step_value, mobility_model, packet_size, gen_rate):
        super().__init__(node_type, step_value, mobility_model)
        self.is_generating = False
        self.next_gen_time = 0

        self.neighbor = None
        self.packet_size = packet_size
        self.gen_rate = gen_rate
        if self.node_type == 0:
            if not isinstance(gen_rate, int):
                raise TypeError(f'Invalid type for Node.gen_rate, {gen_rate}: {type(gen_rate)}')
        self.neighor_counter_updated = False
        self.total_generated_bytes = 0

        self._leftover_packets = None

    def _generate(self, network):
        '''
        Generate the number of packets (and subsequently number of ticks) to be sent
        later in time.
        '''
        if network.tick > self.next_gen_time:
            number_of_packets = np.random.normal(self.gen_rate, scale=self.gen_rate/4) / self.packet_size
            if number_of_packets < 1:
                self._leftover_packets = number_of_packets
            else:
                if self._leftover_packets is None:
                    self._leftover_packets = number_of_packets - int(number_of_packets)
                else:
                    number_of_packets += self._leftover_packets
                    self._leftover_packets = number_of_packets - int(number_of_packets)

                number_of_packets = int(round(number_of_packets))

                temp_generated_bytes = 0
                for _ in range(number_of_packets):
                    fresh_packet = self.create_packet(network, next(self.neighbor))
                    if not fresh_packet is None:
                        temp_generated_bytes += fresh_packet.size
                        self.queue.append(fresh_packet)
                self.total_generated_bytes += temp_generated_bytes

            self.next_gen_time += 1/network.step_value

    def _transmit(self, network):
        try:
            packet = self.queue.pop()
        except IndexError:
            pass
        else:
            packet.next_node.receive(network, packet)
            self.data['transmitted_packets'].append(packet)

    # TODO: Consider different bandwidths
    def transmit(self, network):
        if not self.neighor_counter_updated:
            self.update_neighbor_counter(network)
        self._generate(network)
        self._transmit(network)

    def update_neighbor_counter(self, network):
        self.neighor_counter_updated = True
        self.neighbor = (n for n in itertools.cycle(nx.neighbors(network, self)))

    def reset_values(self):
        self.neighbor_counter_updated = False


#TODO: Documentation!!!!!!!!
class VaryingRelayNode(VaryingTransmitNode):
    def __init__(self, node_type, step_value, mobility_model, packet_size, gen_rate):
        super().__init__(node_type, step_value, mobility_model, packet_size, gen_rate)

        self.neighbor_ok_list_updated = False  # Next tick its ok to send
        self.neighbor_edge_list_updated = False

    def relay(self, network):
        if not self.neighbor_ok_list_updated:
            self.update_neighbor_ok_list(network)

        if not self.neighbor_edge_list_updated:
            self.update_neighbor_edge_list(network)

        if len(self.queue) > 0:
            packet = self.queue[-1]

            try:
                if network.tick >= self.next_ok_tick_for[packet.next_node]:
                    # Update next ok tick
                    self.next_ok_tick_for[packet.next_node] += self.edge_tick_val_for[packet.next_node] / network.step_value

                    packet = self.queue.pop()
                    packet.next_node.receive(network, packet)
                    self.data['relayed_packets'].append(packet)
            except KeyError:
                print(f'Tick: {network.tick}')
                print(f'Relay {self} wants to send {packet} to {packet.next_node}')

                # TODO: Develop retry mechanism
                # Drop packet if not possible to get
                packet = self.queue.pop(); packet.dropped()

    def update_neighbor_ok_list(self, network):
        self.next_ok_tick_for = {neighbor:0 for neighbor in nx.neighbors(network, self)}
        self.neighbor_ok_list_updated = True

    def update_neighbor_edge_list(self, network):
        self.edge_tick_val_for = {e[1]:e[2]['TickValue'] for e in network.edges.data() if e[0] is self}
        self.neighbor_edge_list_updated = True

    def reset_values(self, network):
        self.update_neighbor_edge_list(network)
        self.update_neighbor_ok_list(network)


class RestrictedNode(VaryingRelayNode):
    '''
    Node object that has `restrictions` imposed onto it, such as max buffer size.
    '''
    def __init__(self, node_type, step_value, mobility_model, packet_size, gen_rate, max_buffer_size):
        '''
        :param max_buffer_size: Maximum number of Bytes (!) allowed in device buffer (queue).
        '''
        super().__init__(node_type, step_value, mobility_model, packet_size, gen_rate)
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
