import copy
from collections import deque

class SimpleChannel:
    total_packets_transmitted = 0
    def __init__(self, name, bandwidth, step_m, n_ids=None):
        self.name = name
        self._packets_in_channel = deque()
        self._to_transmit = []
        self._raw_bandwidth = bandwidth
        self.bandwidth = float(bandwidth) * step_m
        self.time = 0
        self.current_channel_load = 0

        # ID of nodes accessing this channel
        if n_ids:
            self.node_id_list = n_ids
        else:
            self.node_id_list = []

        self.data = {'received_packets': [],
                     'sent_packets': [],
                     'dropped_packets': [],
                     }

    def get_packets(self, src, dest):
        '''Get packets in channel that are from "from"
           to "to".

           :param src: Node object
           :param dest: Node object
           :return: list of Packet objects with 'from'-'to' string
                    in path of Packet
        '''
        # Find all packets with correct path and collect into list
        packets_to_return = []
        for packet in self._packets_in_channel:
            if f'{src.id}-{dest.id}' in packet.path:
                packets_to_return.append(packet)

        for p in packets_to_return:
            try:
                self._packets_in_channel.remove(p)
            except ValueError as err:
                raise err

        self.data['sent_packets'].append(packets_to_return)
        return packets_to_return

    def receive(self, packet_list):
        '''Receive packet list and insert into channel (_packets_in_channel)
           and add to counter

           :param packet_list:
           :return:
        '''
        if not self.node_id_list:
            raise Exception(f'{self}.node_id_list is empty!')
        received_packets = []
        to_return = []  # packets to be returned b/c bandwidth full
        for packet in packet_list:
            self._packets_in_channel.append(packet)
            received_packets.append(packet)
        self.data['received_packets'].append(received_packets)
        return to_return

    def update(self):
        while(self._packets_in_channel):
            self._to_transmit.append(self._packets_in_channel.popleft())
        self.time += 1

    def get_other_node_id(self, node_id):
        id_list_copy = copy.copy(self.node_id_list)
        id_list_copy.remove(node_id)
        return id_list_copy.pop()

    def __repr__(self):
        return f'Channel_{self.name}_{str(self.bandwidth)}'

class TestChannel:
    def __init__(self, name, bandwidth, step_m, n_ids=None):
        global packets_sent
        self.name = name
        self.staged = []
        self.pushed = []

        self._raw_bandwidth = bandwidth
        self.bandwidth = float(bandwidth) * step_m
        self.time = 0
        self.current_channel_load = 0

    def get_packets(self, src, dest):
        pass
