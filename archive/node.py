# import simpy
import logging
from archive import packet
import numpy as np
from abc import ABCMeta, abstractmethod

logging.basicConfig(filename="node.log", level=logging.INFO, filemode="w")

class Node(metaclass=ABCMeta):
    current_id = 0
    @staticmethod
    def get_id():
        id = Node.current_id
        Node.current_id += 1
        return id

    def __init__(self, **kwargs):
        self.id = Node.get_id()
        self.time = 0
        logging.info(f"Instantiating Node {self.id}")

    @abstractmethod
    def run(self, env_time):
        pass

    def update_time(self):
        self.time += 1

    def __repr__(self):
        return(f"{self.__class__.__name__}"
                f"(ID: {self.id})")

    def __hash__(self):
        return hash(self.id)

class MovementNode(Node):
    def __init__(self, **kwargs):
        super().__init__()
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.z = kwargs['z']
        self.mobility_model = kwargs['mobility_model']

    def run(self, env_time):
        self.move()

    def move(self):
        if self.mobility_model:
            self.x, self.y, self.z = self.mobility_model(self.x, self.y, self.z)

class TransmittingNode(MovementNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.destinations = kwargs['destinations']
        self.generation_rate = kwargs['generation_rate']
        self.routing_algorithm = kwargs['routing_algorithm']
        self.queue = kwargs['queue']

    def run(self, env_time):
        self.move()
        self.generate(env_time)
        self.update_time()
        self.node += 1 # Should this be here?
        return self.transmit()

    def transmit(self):
        #TODO: Handle multiple possible transmissions
        if self.queue:
            outbound_packet = self.queue.pop()
            print(f"Sending packet {outbound_packet.id} to Node {outbound_packet.destination}")
            return outbound_packet
        else:
            print("Queue is empty")

    def generate(self, env_time):
        # TODO: DO: How to deal with fraction packet generation rates
        # TODO: How to deal with different packet sizes
        # TODO: How to deal with specific destinations
        logging.info(f"{self} generating packet(s)")
        packet_kwargs = {'size': 1,
                         'source':self.id,}
        # TODO: Think more about what exactly should the generation_rate
        # object be? Should it be a lambda? Or a function? I feel like it needs
        # a state. Perhaps it should be able to access the internals of the Node class
        # to be able to make a decision of what the generation rate is? Or perhaps a self
        # defined class that can be catered to a certain application (typical web browser)
        # etc ? <-- sounds like a good idea.
        # for _ in range(next(self.generation_rate)):
        #     rand = np.random.randint(len(self.destinations))
        #     destination = self.destinations[rand]
        #     path = self.routing_algorithm(destination)
        #     packet_kwargs['destination'] = destination
        #     packet_kwargs['path'] = path
        #
        #     self.queue.append(packet.Packet(**packet_kwargs))
        for _ in range(self.generation_rate):
            rand = np.random.randint(len(self.destinations))
            destination = self.destinations[rand]
            path = self.routing_algorithm(destination)
            packet_kwargs['destination'] = destination
            packet_kwargs['path'] = path
            packet_kwargs['transmission_time'] = 1

class ReceivingNode(MovementNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def receive(self,packet_object):
        # Passive node, no need for object detection
        print(f"Received packet {packet_object.id}")

class ReceivingAndTransmittingNode(TransmittingNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def receive(self, packet_object):
        print(f"Received packet object {packet_object.id}")
        if not isinstance(packet.Packet, packet_object):
            print(f"{packet_object} not of type {type(packet.Packet)}")
        else:
            packet_object.current_node = self.id
            self.queue.append(packet_object)

class SimpleGroundNode(ReceivingAndTransmittingNode):
    def __init__(self, **kwargs):
        super().__init__()

class SimpleUAVNode(ReceivingAndTransmittingNode):
    def __init__(self, **kwargs):
        super().__init__()

class SimpleSatelliteNode(ReceivingAndTransmittingNode):
    def __init__(self, **kwargs):
        super().__init__()

if __name__ == "__main__":
    pass
    # env = simpy.Environment()
    # node = Node(env)
    # env.run(until=10)
