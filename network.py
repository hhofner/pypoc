import networkx as nx
from node import Packet, Node


def run_network(ticks):
    network = nx.Graph()

    '''Create the topology'''
    src_nodes = [Node(0), Node(0)]
    relay_nodes_src_side = [Node(1) for _ in range(3)]
    relay_nodes_dest_side = [Node(1) for _ in range(3)]
    dest_nodes = [Node(2), Node(2)]

    c1 = [(src, rel, {'Weight': 1})
          for rel in relay_nodes_src_side for src in src_nodes]

    c2 = [(rel, dest, {'Weight': 1})
          for rel in relay_nodes_dest_side for dest in dest_nodes]

    c3 = [(rel1, rel2, {'Weight': 1})
          for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_src_side]

    network.add_edges_from(c1)
    network.add_edges_from(c2)
    network.add_edges_from(c3)

    tick = 0
    while tick < ticks:
        print(f'~~Time {tick} ~~')
        for node in network.nodes:
            node.run(network)
        tick += 1


if __name__ == '__main__':
    run_network(15)

    print(f'Generated : {Packet.generated_count}')
    print(f'Arrived : {Packet.arrived_count}')
