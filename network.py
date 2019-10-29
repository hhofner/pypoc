import matplotlib.pyplot as plt

import networkx as nx
from node import Packet, Node


class PyPocNetwork(nx.Graph):
    def get(self, key, node1, node2):
        return self[node1][node2][str(key)]
    
    def can_send_through(self, key, node1, node2, bytes, received_edge=None):
        if key != 'Channel':
            print(f'Warning: Did you really mean {key}?')
        
        # print(self[node1][node2])
        v = None
        u = None
        link_found = False
        if not received_edge:
            for edge in self.edges:
                v, u = edge
                if (v is node1 and u is node2) or (v is node2 and u is node1):
                    link_found = True
                    break

            if link_found:
                if self[u][v]['Channel'] + bytes < self[u][v]['Bandwidth']:
                    self[u][v]['Channel'] += bytes
                    print(f'Confirming to be here for Node {node1.id}')
                    return (True, self[u][v])
                else:
                    return (False, self[u][v])
            elif not link_found:
                raise Exception(f'Link not found between {node1} and {node2}')
        
        elif received_edge:
            if received_edge['Channel'] + bytes < received_edge['Bandwidth']:
                received_edge['Channel'] += bytes
                return (True, received_edge)
            else:
                return (False, received_edge)


def run_network(ticks):
    network = PyPocNetwork()

    '''Create the topology'''
    src_nodes = [Node(0), Node(0)]
    relay_nodes_src_side = [Node(1) for _ in range(3)]
    relay_nodes_dest_side = [Node(1) for _ in range(3)]
    dest_nodes = [Node(2), Node(2)]

    c1 = [(src, rel, {'Bandwidth': 200, 'Channel': 0})
          for rel in relay_nodes_src_side for src in src_nodes]

    c2 = [(rel, dest, {'Bandwidth': 200, 'Channel': 0})
          for rel in relay_nodes_dest_side for dest in dest_nodes]

    c3 = [(rel1, rel2, {'Bandwidth': 200, 'Channel': 0})
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

    return network


if __name__ == '__main__':
    net = run_network(20)

    print(f'\tGenerated Packets: {Packet.generated_count}')
    print(f'\ttArrived Packets: {Packet.arrived_count}')

    print(f'\t{"#"*10}Individual Node Data{"#"*10}')
    for n in net.nodes:
        print(n.get_pretty_data())
