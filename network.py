import simpy
import networkx as nx
import node
import numpy as np

class Network:
    def __init__(self, ebunch, env_time, **kwargs):
        self.env = simpy.Environment()
        self.env_time = env_time
        self.nodes = []
        # for bunch in ebunch:
        #     node1, node2, weight = bunch
        #     node1.add_env(self.env)
        #     node2.add_env(self.env)

        # G = nx.Graph()
        # G.add_edges_from(ebunch)

    def run(self):
        pass

    def start(self):
        print("Starting network")
        self.env.run(until=self.env_time)

class HelloNetwork(Network):
    def __init__(self, **kwargs):
        self.env_time = 15
        self.ebunch = [()]
        super().__init__(self.ebunch, self.env_time, **kwargs)
        self.nodes = []

        self.kwargs = {'x':0,
                       'y':0,
                       'z':0,
                       'mobility_model': lambda x,y,z: (x+1, y+1, z+1),
                       'env': self.env,}

        for _ in range(2):
            kwargs = dict(self.kwargs)
            kwargs['x'] = np.random.randint(5)
            kwargs['y'] = np.random.randint(5)
            kwargs['z'] = np.random.randint(5)
            self.nodes.append(node.MovingNode(**kwargs))

if __name__ == "__main__":
    print("Starting test network")
    hello_network = HelloNetwork()
    hello_network.start()
