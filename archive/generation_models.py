import numpy as np
from archive import packet


def basic_linear_generation(node):
    packet_size = 8000 #1kB
    # TODO: SET PACKET PATH WITH SET_PATH() METHOD
    generation_rate = node.config['generation_rate']
    transmission_rate = node.config['transmission_rate']
    destinations = node.config['destinations']

    if transmission_rate <= 0:
        print(f'Warning: Transmission rate is 0')
        return None
    else:
        transmit_rate_current = np.random.normal(transmission_rate)
        for _ in range(transmit_rate_current // packet):
            if not destinations:
                print(f'Warning: no destinations specified for node {node.id}')
                return None
            else:
                rand_dest = np.random.randint(len(destinations))
                new_packet = packet.Packet(node.id, destinations[rand_dest], packet_size)
                new_packet.set_path(node.topology)

                node.queue.append(new_packet)

def basic_normal_generation(node):
    packet_size = 8000  # 1kB
    # TODO: SET PACKET PATH WITH SET_PATH() METHOD
    generation_rate = node.config['generation_rate']
    transmission_rate = node.config['transmission_rate']
    destinations = node.config['destinations']

    if transmission_rate <= 0:
        return None
    else:
        transmit_rate_current = np.random.normal(transmission_rate)
        for _ in range(int(transmit_rate_current // packet_size)):
            if not destinations:
                print(f'Warning: no destinations specified for node {node.id}')
                return None
            else:
                rand_dest = np.random.randint(len(destinations))
                new_packet = packet.Packet(node.id, destinations[rand_dest], packet_size)
                new_packet.set_path(node.topology)

                node.queue.append(new_packet)

def time_experimental_generation(node):
    generation_rate = node.config['generation_rate']
    destinations = node.config['destinations']
    packet_size = 1
    if generation_rate <= 0:
        return None
    else:
        if node.time == 100:
            for _ in range(generation_rate*20):
                if not destinations:
                    print(f'Warning: No destinations available for node {node.id}')
                    return None
                else:
                    rand_int = np.random.randint(len(destinations))
                    new_packet = packet.Packet(node.id, destinations[rand_int], packet_size)
                    new_packet.set_path(node.topology)
                    node.queue.append(new_packet)
        else:
            x = int(np.random.normal(generation_rate, 1))
            for _ in range(x):
                if not destinations:
                    return None
                else:
                    rand_int = np.random.randint(len(destinations))
                    new_packet = packet.Packet(node.id, destinations[rand_int], packet_size)
                    new_packet.set_path(node.topology)
                    node.queue.append(new_packet)