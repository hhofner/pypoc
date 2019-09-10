import networkx as nx
import simple_node
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Network(object):
    def __init__(self, env_time):
        self.env_time = env_time
        self.nodes   = []
        self.network = nx.Graph()
        self.outbound_packets = []
        self.node_values = {}

    def set_up_network(self):
        ebunch = []

        ground_nodes = [simple_node.Node() for _ in range(8)]
        air_nodes = [simple_node.Node() for _ in range(4)]
        sat_nodes = [simple_node.Node()]

        for gn in ground_nodes[:4]:
            for an in air_nodes[:2]:
                ebunch.append((gn.id, an.id, {'Weight':1}))

        for gn in ground_nodes[4:]:
            for an in air_nodes[2:]:
                ebunch.append((gn.id, an.id, {'Weight':1}))

        for an in air_nodes:
            ebunch.append((an.id, sat_nodes[0].id, {'Weight':1}))

        #update transmitting nodes
        destinations = [n.id for n in ground_nodes[4:]]
        for tgn in ground_nodes[:4]:
            tgn.update(**{'destinations':destinations})
            tgn.update(**{'generation_rate': 1})

        self.nodes += ground_nodes
        self.nodes += air_nodes
        self.nodes += sat_nodes

        self.network.add_edges_from(ebunch)

        # Initialize empty data values for each node
        for n in self.nodes:
            self.node_values[n.id] = []

    def run(self):
        if not self.nodes:
            print(f'Error: Network is empty!')
        else:
            while self.env_time > 0:
                for n in self.nodes:
                    possible_packets = n.transmit()
                    if possible_packets:
                        self.outbound_packets += possible_packets

                self.evaluate_transmission()
                self.collect_data()

                self.env_time -= 1

    def evaluate_transmission(self):
        for _ in range(len(self.outbound_packets)):
            outbound_packet = self.outbound_packets.pop()
            path = nx.dijkstra_path(self.network, outbound_packet.source, outbound_packet.destination, weight='Weight')
            outbound_packet.path = path

            next_node = path[1]
            self.nodes[next_node].receive(outbound_packet) #Sketchy TODO: Better solution

            if self.env_time in self.network[path[0]][next_node].keys():
                self.network[path[0]][next_node][self.env_time] += 1
            else:
                self.network[path[0]][next_node][self.env_time] = 1

        for edge in self.network.edges:
            a, b = edge
            self.network[a,b]['Weight'] = self.network[a,b][self.env_time]

    def find_path(self, net, src, dest):
        pass

    def collect_data(self):
        for n in self.nodes:
            self.node_values[n.id].append(len(n.queue))


if __name__ == '__main__':
    network = Network(25)
    network.set_up_network()
    network.run()
    data = pd.DataFrame(network.node_values)
    print(data)
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
    nx.draw(network.network, with_labels=True, ax=ax1)
    data.plot(ax=ax2)
    plt.show()