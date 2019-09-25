from math import log2

class Channel(object):
    def __init__(self, bandwidth, sinr, tsv):
        self._capacity = bandwidth * log2(1 + sinr) #bits per second
        self._time_step_value = tsv
        self._time_step_capacity = self._capacity * self._time_step_value

        self.capacity_current = self._time_step_capacity
        self.packets_current = []
        self.dropped_packets_current = 0

    def access(self, packets):
        self.dropped_packets_current = 0
        for packet in packets:
            if packet.size < self.capacity_current:
                self.packets_current.append(packet)
                self.capacity_current -= packet.size
            else:
                packet_curr_index = packets.index(packet)
                rest_of_packet_count = len(packets[packet_curr_index:])
                self.dropped_packets_current = rest_of_packet_count
                break


    def _get_list_of_outbound_packets(self):
        '''
        Get a list of all packets that have finished their travel through their
        respective link. In this method, the user can implement their desired
        propagation delay. Default for now is just return the current list. The
        channel capacity must also be 'reset'.

        :return: List[Packet] , List of Packet objects
        '''
        outboud_packets = self.packets_current
        self.packets_current = []
        self.capacity_current = self._time_step_capacity

        return outboud_packets

    @property
    def outbound_packets(self):
        return self._get_list_of_outbound_packets()