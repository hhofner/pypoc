from math import log2
from collections import deque


class SimpleChannel:
    def __init__(self, name, bandwidth, time_equivalent):
        self.name = name
        self._packets_in_channel = deque()
        self._to_transmit = deque()
        self._raw_bandwidth = bandwidth
        self.bandwidth = float(bandwidth) * time_equivalent
        self.time = 0

        self.current_channel_load = 0

        self.data = {'received_packets': [],
                     'sent_packets': [],
                     'dropped_packets': [],
                     }

    def get_packets(self, src, dest):
        '''Get packets in channel that are from "from"
           to "to".

           :param src; Node object
           :param dest; Node object
           :return; list of Packet objects with 'from'-'to' string
                    in path of Packet
        '''
        packets_to_return = []
        for packet in self._to_transmit:
            if f'{src.id}-{dest.id}' in packet.path:
                packets_to_return.append(packet)
                self.current_channel_load -= packet.size
                if self.current_channel_load < 0:
                    # raise Exception(f'Channel load below 0')
                    pass
        self.data['sent_packets'].append(packets_to_return)
        return packets_to_return

    def receive(self, packet_list):
        '''Receive packet list and insert into channel (_packets_in_channel)
           and add to counter
        '''
        received_packets = []
        for packet in packet_list:
            if self.current_channel_load < self.bandwidth:
                self._packets_in_channel.append(packet)
                self.current_channel_load += packet.size
                print(f'chan_load: {self.current_channel_load}')
                received_packets.append(packet)
            elif self.current_channel_load > self.bandwidth:
                break
        self.data['received_packets'].append(received_packets)

    def update(self):
        for packet in self._packets_in_channel:
            self._to_transmit.append(packet)
        self.time += 1

    def __repr__(self):
        return f'Channel_{self.name}_{str(self.bandwidth)}'
