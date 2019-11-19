import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import itertools
import seaborn as sns
import pandas as pd

import networkx as nx
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode

verbose = True
verboseprint = print if verbose else lambda *a, **k: None


class PyPocNetwork(nx.Graph):
    def get(self, key, node1, node2):
        return self[node1][node2][str(key)]
    
    def can_send_through(self, key, node1, node2, bytes, received_edge=None):
        if key != 'Channel':
            input(f'Warning: Did you really mean {key}?')
        
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
                    verboseprint(f'Creating link reference {node1}->{node2}')
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

    def reset_bandwidths(self):
        #TODO: Consider, at the end of every tick do we reset the load number
        # on each channel? Given that, what will happen next tick? And does this
        # make sense ?
        for edge in self.edges:
            v, u = edge
            self[v][u]['Channel'] = 0


def run_network(ticks, trate=None, rrate=None):
    transmit_rate = trate if trate else 1
    relay_rate = rrate if rrate else 1
    network = PyPocNetwork()

    '''Create the topology'''
    src_nodes = [VaryingTransmitNode(0, 1, transmit_rate, 1)]
    relay_nodes_src_side = [Node(1) for _ in range(3)]
    relay_nodes_dest_side = [Node(1) for _ in range(3)]
    dest_nodes = [Node(2), Node(2)]

    c1 = [(src, rel, {'Bandwidth': 50, 'Channel': 0})
          for rel in relay_nodes_src_side for src in src_nodes]

    c2 = [(rel, dest, {'Bandwidth': 50, 'Channel': 0})
          for rel in relay_nodes_dest_side for dest in dest_nodes]

    c3 = [(rel1, rel2, {'Bandwidth': 50, 'Channel': 0})
          for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_src_side]

    network.add_edges_from(c1)
    network.add_edges_from(c2)
    network.add_edges_from(c3)

    tick = 0
    while tick < ticks:
        print(f'~~Time {tick} ~~')
        for node in network.nodes:
            print(f'Accessing node: {node}')
            node.run(network)
        tick += 1
        network.reset_bandwidths()

    return network


if __name__ == '__main__':
    # net = run_network(10)

    # print(f'\tGenerated Packets: {Packet.generated_count}')
    # print(f'\ttArrived Packets: {Packet.arrived_count}')

    # print(f'\t{"#"*10}Individual Node Data{"#"*10}')
    # for n in net.nodes:
    #     print(n.get_pretty_data())

    ## Plotting ##
    # fig, ax = plt.subplots()

    sns.set()
    sns.set_style('whitegrid')
    sns.set_context('poster')
    fig, (ax1, ax2) = plt.subplots(1,2)
    palette = itertools.cycle(sns.color_palette())

    patches = []
    # for n in net.nodes:
    #     if n.type == 1:
    #         now_color = next(palette)
    #         queue_lengths = n.data['queue_size']
    #         plt.plot(queue_lengths, color=now_color)
    #         patches.append(mpatches.Patch(color=now_color, label=n))
    # plt.legend(handles=patches)

    ## Throughput Plotting ##
    queue_sizes = []
    throughputs = []
    for tr in range(4, 32, 4):
        net = run_network(20, trate=tr)
        temp = []
        for node in net:
            temp.append(len(node.queue))
        queue_sizes.append(temp)
        throughputs.append(Packet.arrived_count/Packet.generated_count)
        Packet.reset()
    
    data = pd.Series(throughputs)
    ax = sns.lineplot(data=data, ax=ax1)
    ax.set(title='Throughput Performance')

    # fig, ax = plt.subplots()

plt.show()
