from math import log2

class Channel:
    def __init__(self, name, time_step, bandwidth, sinr):
        self.name = name
        self.bandwidth = bandwidth
        self.sinr = sinr
        self.true_capacity = bandwidth * log2(1 + sinr)
        self.capacity = int(self.true_capacity * time_step) #bits per time step
        print(f'Instantiating {self.name} channel with channel capacity: {self.true_capacity} bps')

        self.held_packets = [] #data contained in the channel
        self.metadata = {'dropped_packets': 0}

    def transmit_access(self, packet_list):
        current_held_bits = self._get_packet_list_sum(self.held_packets)
        for packet in packet_list:
            if current_held_bits > self.capacity:
                self.metadata['dropped_packets'] += 1
            else:
                current_held_bits += packet.size
                self.held_packets.append(packet)

    def receive_access(self, src, dest):
        packets_to_return = []
        for packet in self.held_packets:
            if f'{src.id}-{dest.id}' in packet.path:
                packets_to_return.append(packet)
        return packets_to_return

    def _get_packet_list_sum(self, packet_list):
        total_sum = 0
        for packet in packet_list:
            total_sum += packet.size

        return total_sum