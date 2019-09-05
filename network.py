import simpy
import networkx as nx
import node
import numpy as np
from abc import ABCMeta, abstractmethod

class Network:
    def __init__(self, ebunch=[], env_time=0, **kwargs):
        self.env = simpy.Environment()
        self.env_time = env_time
        self.nodes = []

    @abstractmethod
    def run(self):
        pass

class HelloNetwork(Network):
    def __init__(self, **kwargs):
        super().__init__()
        self.env_time = 15
        self.ebunch = [()]
        self.nodes = []
        self.outbound_packets = []

        self.node_kwargs = {'x':0,
                            'y':0,
                            'z':0,
                            'mobility_model': lambda x,y,z: (x+1, y+1, z+0),
                            'packet_rate': 0,
                            'transmission_range': 0,
                            'queue': [],
                            }

        # 3 Receiving nodes
        for _ in range(3):
            kwargs = dict(self.node_kwargs)
            kwargs['x'] = np.random.randint(5)
            kwargs['y'] = np.random.randint(5)
            kwargs['z'] = np.random.randint(5)
            self.nodes.append(node.ReceivingNode(**kwargs))

        # 1 Transmitting Node
        self.node_kwargs['destinations'] = [node.id for node in self.nodes]
        self.node_kwargs['generation_rate'] = (i for i in range(100))
        self.node_kwargs['routing_algorithm'] = self.one_hop_routing()
        self.nodes.append(node.TransmittingNode(**self.node_kwargs))

    def one_hop_routing(self):
        destination_nodes = [node.id for node in self.nodes]
        def routing(destination):
            if destination in destination_nodes:
                return [destination]
        return routing

    def run(self):
        print("Running")
        print(f"{self.nodes}")
        while self.env_time > 0:
            print("yes")
            for node in self.nodes:
                print(f"Node {node.id}")
                possible_packet = node.run()
                if possible_packet:
                    self.outbound_packets.append(possible_packet)
            node_ids = [node.id for node in self.nodes]
            for packet in list(self.outbound_packets):
                for node in self.nodes:
                    print("Checking destinations")
                    if node.id == packet.destination:
                        try:
                            node.receive(packet)
                            self.outbound_packets.remove(packet)
                        except Exception as err:
                            raise(err)

            self.env_time -= 1

if __name__ == "__main__":
    print("Starting test network")
    hello_network = HelloNetwork()
    hello_network.run()
