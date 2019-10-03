from typing import List, Optional
import networkx as nx

class Packet:
    current_id = 0
    @staticmethod
    def get_id():
        id = Packet.current_id
        Packet.current_id += 1
        return id

    def __init__(self, source, destination, size):
        self.id = Packet.get_id()

        self.source          = source
        self.destination     = destination
        self._initial_source = source
        self.size: int       = size

        self.routing_algorithm = None
        self.path: Optional[List[int]] = None

    def set_path(self, graph):
        if not self.path:
            if not self.routing_algorithm:
                self.path = nx.dijkstra_path(graph, self.source, self.destination)
            else:
                raise Exception('Have not implemented routing decision from packet yet')

    def next_hop(self):
        if not self.path[0] == self.source:
            raise Exception(f'Path problems, first node on path and source IDs do not match!'
                            f'{self.source} =/= {self.path[0]}')
        return self.path[1]

    def set_current_node(self, current):
        if current == self.path[1]:
            self.source = current
            self.path.pop(0)
        elif current == self.path[0]:
            print(f'Warning: Packet has not moved from {self.source}')
        else:
            raise Exception(f'Current Node {current} does not match packet {self.id} next hop: {self.path[1]}'
                            f' or current node {self.path[0]}')

    def __repr__(self):
        s = f'Packet({self.id}, init_source:{self._initial_source}, current_source: {self.source}, dest:{self.destination}'
        s += f' path:{self.path})'

        return s
