'''
methods module -- this module contains special methods for the three most
important Node methods, namely: generate, transmit and receive.

author: Hans Hofner
'''
import random
import networkx as nx


def get_string_path(path):
    return ('-'.join(str(n.id) for n in path))


class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

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
        self.is_dropped = False
        self.has_arrived = False
        self.id = Packet.generated_count
        self.generated()

    def __del__(self):
        pass

    def dropped(self):
        if not self.is_dropped:
            Packet.dropped_count += 1
        self.is_dropped = True

    def arrived(self):
        if not self.has_arrived:
            Packet.arrived_count += 1
        self.has_arrived = True

    def generated(self):
        Packet.generated_count += 1

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

    def __repr__(self):
        return f'Packet{str(self.id)}|{self.path}'


def simple_generate(node, network, rate):
    '''
    Generate packets and push onto the nodes queue. Uses a passed in
    network object to figure out route for generated packets.

    :param node: SimpleNode object
    :param network: A networkx Graph object instance
    :param rate: Int, num of packets to be generated.
    :return:
    '''
    if not node.destinations:
        raise Exception(f'No destinations or '
                        f'network declared for Node {node.id}')

    generated_count = 0
    generated_packets = []
    while generated_count < rate:
        packet_size = 1
        src = node
        dest = random.choice(node.destinations)

        path = get_string_path(nx.dijkstra_path(network,
                               src, dest, 'Weight'))
        print(path)

        new_packet = Packet(packet_size, src, dest, path)
        generated_packets.append(new_packet)
        generated_count += 1

        node.queue.extend(generated_packets)
        node.data['generate_packet_list'].append(generated_packets)


def simple_transmit(node, rate, next_node_id):
    '''
    Return a list of packets fetched from the nodes queue
    with a total bit count of more or less the nodes
    transmit rate.

    :param node:
    :param rate:
    :param next_node_id:
    :return: List of Packet tuples, can be empty
    '''
    packets_to_transmit = []
    for _ in range(rate):
        for packet in node.queue:
            if str(next_node_id) in packet.path:
                packets_to_transmit.append(packet)
                node.queue.remove(packet)
                break

    node.data['sent_packet_list'].append(packets_to_transmit)
    return packets_to_transmit


def simple_receive(node, received_packets):
    '''
    Receive a list of packets and insert them into the
    queue one by one until the total inserted more than or equal
    to the queue max size, or until the list is finished.
    :param packets: list of Packet tuples
    :return:
    '''
    curr_q_size = len(node.queue)
    inserted_packets = []
    dropped_packets = []
    for packet in received_packets:
        if curr_q_size <= node.max_queue_size:
            curr_q_size += packet.size
            node.queue.append(packet)

            node.data['receive_count'] += 1
            inserted_packets.append(packet)
            if node.type == 'dest':
                print('yes!!')
                packet.arrived()
        else:
            node.data['drop_count'] += 1
            dropped_packets.append(packet)
            packet.dropped()
    node.data['drop_packet_list'].append(dropped_packets)
    node.data['receive_packet_list'].append(received_packets)
