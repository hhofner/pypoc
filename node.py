# import simpy
import logging
import packet
import numpy as np
from exceptions import RunMethodEmpty
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
    def run(self):
        pass

    def update_time(self):
        self.time += 1

class MovementNode(Node):
    def __init__(self, **kwargs):
        super().__init__()
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.z = kwargs['z']
        self.mobility_model = kwargs['mobility_model']

    def run(self):
        self.move()

    def move(self):
        self.x, self.y, self.z = self.mobility_model(self.x, self.y, self.z)

class TransmittingNode(MovementNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.destinations = kwargs['destinations']
        self.generation_rate = kwargs['generation_rate']
        self.routing_algorithm = kwargs['routing_algorithm']
        self.queue = kwargs['queue']

    def run(self):
        self.move()
        self.generate()
        self.update_time()
        return self.transmit()

    def transmit(self):
        #TODO: Handle multiple possible transmissions
        if self.queue:
            outbound_packet = self.queue.pop()
            print(f"Sending packet {outbound_packet.id} to Node {outbound_packet.destination}")
            return outbound_packet
        else:
            print("Queue is empty")

    def generate(self):
        # TODO: DO: How to deal with fraction packet generation rates
        # TODO: How to deal with different packet sizes
        # TODO: How to deal with specific destinations
        print(f"generating")
        packet_kwargs = {'size': 1,
                         'source':self.id,}
        for _ in range(next(self.generation_rate)):
            rand = np.random.randint(len(self.destinations))
            destination = self.destinations[rand]
            path = self.routing_algorithm(destination)
            packet_kwargs['destination'] = destination
            packet_kwargs['path'] = path

            self.queue.append(packet.Packet(**packet_kwargs))


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
            self.queue.append(packet_object)

if __name__ == "__main__":
    pass
    # env = simpy.Environment()
    # node = Node(env)
    # env.run(until=10)
