from math import log2
import copy

class Channel():
    def __init__(self, bandwidth, sinr, tsv):
        self._capacity = bandwidth * log2(1 + sinr) #bits per second
        self._time_step_value = tsv

        self.capacity_current = copy.copy(self._capacity)
        self.packets_current = []
        self.dropped_packets_current = 0

    def access_through(self, packets):
        self.dropped_packets_current = 0
        cap_current = self.capacity_current
        for packet in packets:
            if packet.size < cap_current:
                self.packets_current.append(packet)
                cap_current -= packet.size
            else:
                packet_curr_index = packets.index(packet)
                rest_of_packet_count = len(packets[packet_curr_index:])
                self.dropped_packets_current = rest_of_packet_count
                self.capacity_current = cap_current
                break


    def _get_list_of_outbound_packets(self):
        '''
        Get a list of all packets that have finished their travel through their
        respective link. In this method, the user can implement their desired
        propagation delay. Default for now is just return the current list. The
        channel capacity must also be 'reset'.

        :return: List[Packet] , List of Packet objects
        '''
        outbound_packets = self.packets_current
        self.packets_current = []
        self.capacity_current = self._capacity

        return outbound_packets

    @property
    def outbound_packets(self):
        return self._get_list_of_outbound_packets()