import logging
import networkx as nx
import node
import numpy as np
from abc import ABCMeta, abstractmethod

logging.basicConfig(filename="network_run.log", level=logging.INFO, filemode="w")
class Network(metaclass=ABCMeta):
    def __init__(self, ebunch=[], env_time=0, **kwargs):
        self.env_time = env_time
        self.ebunch = ebunch
        self.nodes = []

        logging.info(f"Instantiating {self.__class__.__name__}")
        self.set_up()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def set_up(self):
        pass

    def __repr__(self):
        return(f'{self.__class__.__name__}'
                f'Nodes: {len(self.nodes)}')

class RunningNetwork(Network):
    def __init__(self, ebunch=[], env_time=0, **kwargs):
        super().__init__(ebunch, env_time, **kwargs)
        self.outbound_packets = []

    # Ideas about making set up some type of class or static function(!!)
    # that can be called by other classes. This would allow for other classees
    # who want to use several different class set ups (you don't have to)
    # build so often.
    def set_up(self):
        ''' Method to set up network topology. This method should be easily
            called by child instances to build on top of topologies, and is
            expected to be overriden (with super() calls).

            :return: None
        '''
        logging.info(f"Setting up {self}")
        logging.info(f"Finish setting up {self}")

    def run(self):
        logging.info(f"Running Network {self}")
        if self.env_time == 0:
            print(f"Warning: env_time variable is 0!")
            logging.warning(f'{self}.env variable is 0')
        elif self.env > 0:
            while(self.env > 0):
                # Collect all outbound packets and call all nodes run() method.
                for node in self.nodes:
                    possible_packets = node.run(self.env)
                    if possible_packet:
                        self.outbound_packets + = list(possible_packet)

                for packet in list(self.outbound_packets):
                    destination = packet.next_hop()
                    if self.nodes[destination]:
                        receiving_node = self.nodes[destination]
                        self.evaluate_transmission(packet, receiving_node)
                self.env -= 1

    def evaluate_transmission(self, outbound_packet, destination_node):
    ''' Method to \'evaluate\' the transmission of a packet dependent on factors such as
        channel medium, link quality, transmission time, etc, as well as managing the state
        of outbound packets.
        :param outbound_packet: Packet object to be transmitted.
        :param destination: Receiving Node object.
        :return: None
    '''
        try:
            destination_node.receive(outbound_packet)
            self.outbound_packets.remove(outbound_packet)
        except:
            raise #TODO: Forgot how this works exactly

    def one_hop_routing(self):
        destination_nodes = [node.id for node in self.nodes]
        def routing(destination):
            if destination in destination_nodes:
                return [destination]
        return route_path

class SimpleSAGIN(RunningNetwork):
    def __init__(self, ebunch=[], env_time=0, **kwargs):
        super().__init__()

    def set_up(self):
        node_kwargs = {'x': 0,
                        'y': 0,
                        'z': 0,
                        'mobility_model': None,
                        'destinations': [],
                        'generation_rate': 1,
                        'routing_algorithm': None,
                        'queue': []}
        # Transmitting Ground Nodes
        num_transmit_node = 3
        for _ in range(num_transmit_node):
            temp = node.TransmittingNode(node_kwargs)
            pass



if __name__ == "__main__":
    print("Starting test network")
    hello_network = HelloNetwork()
    hello_network.run()
