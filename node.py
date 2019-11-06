from collections import deque, defaultdict
import matplotlib.pyplot as plt
import random

import networkx as nx

verbose = True
verboseprint = print if verbose else lambda *a, **k: None


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
        self.wait_queue = deque()
        self.queue = deque()

        self.type = type
        self.time = 0

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
        if not self.dest_node_list:
            self.update_dest_node_list(network)
        dest = random.choice(self.dest_node_list)
        path = nx.shortest_path(network, self, dest)
        packet = Packet(path)

        # `can_send_through()` returns Tuple, (Bool, edge)
        can_send, edge = network.can_send_through('Channel', 
                                                  self,
                                                  packet.next_node,
                                                  packet.size,
                                                  self.edges[packet.next_node])
        if can_send:
            self.data['transmited_packets'].append(packet)
            self.edges[packet.next_node] = edge
            packet.next_node.receive(packet)
            verboseprint(f'{self} Sending {packet} to {packet.next_node}')
        else:
            self.edges[packet.next_node] = edge
            input(f'Can not sent data for Node {self.id}')

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

        if self.queue:
            packet = self.queue[0]
            can_send, edge = network.can_send_through('Channel', 
                                                      self, 
                                                      packet.next_node, 
                                                      packet.size, 
                                                      self.edges[packet.next_node])
            if can_send:
                popped_packet = self.queue.popleft()
                self.edges[packet.next_node] = edge
                self.data['relayed_packets'].append(popped_packet)
                popped_packet.next_node.receive(popped_packet)
            else:
                self.edges[packet.next_node] = edge
                print(f'Can not relay for {self}')    

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
            self.transmit_limited(network, 5)
        elif self.type == 1:
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

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return (self.__class__ == other.__class__
               and self.id == other.id)

    def  __str__(self):
        return f'Node {self.id}'

    def __repr__(self):
        return f'(Node id:{self.id},t:{self.type})'


class VaryingTransmissionNode(Node):
    def __init__(self, type, time_conversion, transmit_rate, packet_size_list):
        '''
        '''
        super().__init__(type)
        self.transmit_rate = transmit_rate * time_conversion
        self.packet_size_list = packet_size_list

    def transmit(self, network):
        for _ in range(self.transmit_rate):
            super().transmit(network)
