import numpy as np
import packet

def basic_linear_generation(node):
    generation_rate = node.config['generation_rate']
    destinations = node.config['destinations']
    if generation_rate <= 0:
        return None
    else:
        for _ in range(generation_rate):
            if not destinations:
                return None
            else:
                rand_int = np.random.randint(len(destinations))
                node.queue.append(packet.Packet(node.id, destinations[rand_int]))

def basic_normal_generation(node):
    generation_rate = node.config['generation_rate']
    destinations = node.config['destinations']
    if generation_rate <= 0:
        return None
    else:
        if 'standard_dev' in node.config.keys():
            scale = node.config['standard_dev']
        else:
            scale = int(generation_rate/4)

        packet_rate = int(np.random.normal(generation_rate, scale))
        packet_rate = 0 if packet_rate < 0 else packet_rate

        for _ in range(packet_rate):
            if not destinations:
                return None
            else:
                rand_int = np.random.randint(len(destinations))
                node.queue.append(packet.Packet(node.id, destinations[rand_int]))

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
                    return None
                else:
                    rand_int = np.random.randint(len(destinations))
                    node.queue.append(packet.Packet(node.id, destinations[rand_int], packet_size))
        else:
            x = int(np.random.normal(generation_rate, 1))
            for _ in range(x):
                if not destinations:
                    return None
                else:
                    rand_int = np.random.randint(len(destinations))
                    node.queue.append(packet.Packet(node.id, destinations[rand_int], packet_size))