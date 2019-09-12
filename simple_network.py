import networkx as nx
import simple_node
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class Network(object):
    '''
    Main class responsible for creating and running a simulation instance of a network, as well as
    handling the logic for outbound packets (packets being transmitted).

    The network object expects an 'environment time' argument when being initialized. This parameter indicates how
    many time steps the network will run for.
    '''
    def __init__(self, env_time):
        self.env_time = env_time
        self.nodes   = []
        self.network = nx.Graph()
        self.outbound_packets = []
        self.node_values = {}

        # ndarray to keep values of all node weights at each time point
        self.weight_matrix = None

    @staticmethod
    def default_sagin(ground_node_count=8, air_node_count=6, space_node_count=2):
        nodes  = []
        ebunch = []

        ground_nodes = [simple_node.Node(**{'type': 'ground'}) for _ in range(ground_node_count)]
        air_nodes = [simple_node.Node(**{'type': 'air'}) for _ in range(air_node_count)]
        sat_nodes = [simple_node.Node(**{'type': 'space'}) for _ in range(space_node_count)]

        for gn in ground_nodes[:4]:
            for an in air_nodes[:3]:
                ebunch.append((gn.id, an.id, {'Weight': 1}))

        for gn in ground_nodes[4:]:
            for an in air_nodes[3:]:
                ebunch.append((gn.id, an.id, {'Weight': 1}))

        for an in air_nodes:
            for sn in sat_nodes:
                ebunch.append((an.id, sn.id, {'Weight': 1}))

        # update transmitting nodes
        destinations = [n.id for n in ground_nodes[4:]]
        for tgn in ground_nodes[:4]:
            tgn.update(**{'destinations': destinations})
            tgn.update(**{'generation_rate': 1})

        # update relaying nodes
        for an in air_nodes:
            an.update(**{'serv_rate': 5})
        for sn in sat_nodes:
            sn.update(**{'serv_rate': 7})

        nodes += ground_nodes
        nodes += air_nodes
        nodes += sat_nodes

        return (ebunch, nodes)

    def set_up_network(self):
        '''

        :return: None
        '''
        ebunch, temp_nodes = Network.default_sagin()

        self.nodes += temp_nodes
        self.network.add_edges_from(ebunch)

        # Initialize empty data values for each node
        for n in self.nodes:
            self.node_values[n.id] = []

        #Initialize Weight Matrix
        self.weight_matrix = np.ones((self.env_time, len(self.nodes), len(self.nodes)))

    def run(self):
        if not self.nodes:
            raise Exception(f'Error: Network is empty! Please set up the network by calling the method set_up().')
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
        # Evaluate packet destinations and overwrite their paths at every point
        for _ in range(len(self.outbound_packets)):
            outbound_packet = self.outbound_packets.pop()
            path = nx.dijkstra_path(self.network, outbound_packet.source, outbound_packet.destination, weight='Weight')
            outbound_packet.path = path

            next_node = path[1]
            self.nodes[next_node].receive(outbound_packet) #Sketchy TODO: Better solution

            # At every env_time point, update amount of packets being sent through
            # edge path[0], path[1]
            self.weight_matrix[self.env_time-1][path[0]][path[1]] += 1
            self.weight_matrix[self.env_time-1][path[1]][path[0]] += 1

        # Update edge values according to the number of packets
        # being sent through that edge at the previous time
        for edge in self.network.edges:
            u, v = edge
            try:
                self.network.edges[u,v]['Weight'] = self.weight_matrix[self.env_time - 1][u][v]
            except Exception as err:
                raise

    def find_path(self, net, src, dest):
        pass

    def collect_data(self):
        for n in self.nodes:
            self.node_values[n.id].append(len(n.queue))


if __name__ == '__main__':
    network = Network(50)
    network.set_up_network()
    network.run()
    data = pd.DataFrame(network.node_values)
    print(data)

    sns.set()
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))

    nx.draw(network.network, with_labels=True, ax=ax1)
    ax1.set_title("Network Overview")

    ax2.set(ylim=(0, 8))
    data[9:15].plot(ax=ax2)
    ax2.set_title("Edge Weights = Packets Transmitted Through Edge")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Num of Packets in Queue")
    plt.show()