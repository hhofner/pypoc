from collections import deque, namedtuple, defaultdict
import networkx as nx
import numpy as np
import random
import math


class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

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

    def __init__(self, time_step, packet_size, queue_size, transmit_rate,
                 gen_rate, destinations=None, type=None):
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

        self.metadata = defaultdict(int)
        self.metadata.update({'drop_packet': [],
                              'receive_packet': [],
                              'receive_count': 0,
                              'sent_count': 0,
                              'generate_packet': [],
                              'byte_send': []})

        self.gen_nokori = 0  # This is a "left-over" counter
        self.transmit_nokori = 0

    def transmit_to(self):
        '''
        Return a list of packets fetched from the nodes queue
        with a total bit count of more or less the nodes
        transmit rate.

        :return: List of Packet tuples, can be empty
        '''
        print(f'Node-{self.id} transmitting')
        packets_to_transmit = []
        if self.transmit_nokori > 0 and self.transmit_nokori < 1:
            self.transmit_nokori += np.random.normal(self.transmit_rate)
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
        current_size = self._get_current_queue_size()
        for packet in received_packets:
            if current_size <= self.queue_max_size:
                current_size += packet.size
                self.queue.append(packet)
                self.metadata['receive_count'] += 1
                self.metadata['receive_packet'].append(packet)
                print(self.type)
                if self.type == 'dest':
                    Packet.arrived()
            else:
                self.metadata['drop_packet'].append(packet)
                packet.dropped()

    def generate(self, network):
        '''
        Generate packets and push onto the nodes queue. Uses a passed in
        network object to figure out route for generated packets.

        :param network: A networkx Graph object instance
        :return:
        '''
        if self.gen_rate > 0:
            generated_packets = []
            if not self.destinations:
                raise Exception(f'No destinations or '
                                f'network declared for Node {self.id}')
            self.gen_nokori += np.random.normal(self.gen_rate)  # TODO: Logic?

            packet_size = self.packet_size
            while (self.gen_nokori > 1):
                src = self
                dest = random.choice(self.destinations)

                path = self._get_string_path(nx.dijkstra_path(network,
                                             src, dest, 'Weight'))

                # print(nx.shortest_path(network, src, dest, 'Weight'))
                # input(f'Path for {src.id} to {dest.id}: {path} from ')

                new_packet = Packet(packet_size, src, dest, path)
                generated_packets.append(new_packet)
                self.gen_nokori = self.gen_nokori - 1  #TODO: Rethink logic
                if self.gen_nokori < 0:
                    raise Exception('gen_nokori is less than zero')
            self.metadata['generate_packet'].append(generated_packets)
            self.queue.extend(generated_packets)
        else:
            # self.metadata['generate_packet'].append([None])
            pass

    def _get_current_queue_size(self):
        current_size = 0
        for node in self.queue:
            current_size += node.size

        return current_size

    def get_string_path(self, path):
        return ('-'.join(str(n.id) for n in path))

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        if not self.type:
            return f'Node {self.id}'
        else:
            return f'Node[{self.type}]-{self.id}'


class MultipleChannelNode(Node):
    def __init__(self, time_step, packet_size, queue_size,
                 transmit_rate, gen_rate, destinations=None,
                 type=None, channel_interface_list=None):
        '''
        Initialize a Node object with support for multiple channels. Even ratio
        numbers are assigned to each channel in self.channel_interface_dict.

        :param time_step:
        :param queue_size:
        :param transmit_rate:
        :param gen_rate:
        :param destinations: List of Node objects, optional
        :param type: String denoting type of Node object, optional
        :param channel_interface_list: List of (String) names of channels the
                                       Node object can use/has access to
        '''

        super().__init__(time_step, packet_size, queue_size,
                         transmit_rate, gen_rate, destinations,
                         type)

        self.channel_interface_dict = {}
        for channel in channel_interface_list:
            self.channel_interface_dict[channel] = \
                1/len(channel_interface_list)

    def transmit_to(self, channel_list):
        '''

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

        packets_to_transmit_per_channel = defaultdict(None)
        if len(packets_to_transmit) > len(self.channel_interface_dict.keys()):
            for key in self.channel_interface_dict.keys():
                i = int(self.channel_interface_dict[key] * len(packets_to_transmit))
                for _ in range(i):
                    try:
                        packets_to_transmit_per_channel[key] = packets_to_transmit.pop()
                    except:
                        break

            # input(f'packets_to_transmit_per_channel: {packets_to_transmit_per_channel}')
            for chan in channel_list:
                try:
                    chan.transmit_access([packets_to_transmit_per_channel[chan.name]]) # Need to pass list to transmit access
                except:
                    print(f'Couldnt find for {chan.name}')
        else:
            channel_list[0].transmit_access(packets_to_transmit)


class ImprovedMultipleChannelNode(Node):
    def __init__(self, time_step, packet_size, queue_size,
                 transmit_rate, gen_rate, destinations=None,
                 type=None, channel_interface_list=None):
        '''
        Initialize a Node object with support for multiple channels. Even ratio
        numbers are assigned to each channel in self.channel_interface_dict.

        :param time_step:
        :param queue_size:
        :param transmit_rate:
        :param gen_rate:
        :param destinations: List of Node objects, optional
        :param type: String denoting type of Node object, optional
        :param channel_interface_list: List of (String) names of channels the
                                       Node object can use/has access to
        '''
        super().__init__(time_step, packet_size, queue_size,
                         transmit_rate, gen_rate, destinations,
                         type)
        self.channel_interface_dict = {}
        for channel in channel_interface_list:
            self.channel_interface_dict[channel] = \
                        1/len(channel_interface_list)

    def transmit_to(self, channel_list):
        '''
        Return a list of packets fetched from the nodes queue
        with a total bit count of more or less the nodes
        transmit rate.

        :return: List of Packet tuples, can be empty
        '''
        print(f'Node {self.id} transmitting')
        packets_to_transmit = []
        if self.transmit_nokori > 0 and self.transmit_nokori < 1:
            self.transmit_nokori += self.transmit_rate
        else:
            self.transmit_nokori = np.random.normal(self.transmit_rate)
        to_send_bit_count = 0  # Var to check how much is to be sent
        while(self.transmit_nokori > 1):
            try:
                packet = self.queue.popleft()
            except IndexError as err:
                break
            else:
                to_send_bit_count += packet.size
                packets_to_transmit.append(packet)
            self.transmit_nokori = self.transmit_nokori - 1  # TODO: logic
        total_size = 0

        for p in packets_to_transmit:
            total_size += p.size
            self.metadata['sent_count'] += 1  # Packet count
        self.metadata['byte_send'].append(total_size)  # Exact bit count

        # Decide how many packets sent to each channel
        packets_to_transmit_per_channel = defaultdict(None)
        if len(packets_to_transmit) > len(self.channel_interface_dict.keys()):
            for key in self.channel_interface_dict.keys():
                i = int(self.channel_interface_dict[key] * len(packets_to_transmit))
                for _ in range(i):
                    try:
                        packets_to_transmit_per_channel[key] = \
                            chpackets_to_transmit.pop()
                    except Exception:
                        break

            for chan in channel_list:
                try:
                    chan.receive([packets_to_transmit_per_channel[chan.name]])  # Need to pass list to transmit access
                except Exception:
                    print(f'Couldnt find for {chan.name}')
        else:
            channel_list[0].receive(packets_to_transmit)
