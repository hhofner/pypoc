import packet
import numpy as np

class Node(object):
    current_id = 0
    @staticmethod
    def get_id():
        id = Node.current_id
        Node.current_id += 1
        print(f'Instantiating Node {id}')
        return id

    def __init__(self, **kwargs):
        self.id    = Node.get_id()
        self.queue = []

        self.config = {'generation_rate': 0,
                       'destinations': []}
        self.update(**kwargs)

    def update(self, **kwargs):
        for key in kwargs.keys():
            if key in self.config.keys():
                if isinstance(kwargs[key], type(self.config[key])):
                    self.config[key] = kwargs[key]

        self.generation_rate = self.config['generation_rate']
        self.destinations = self.config['destinations']

    def transmit(self):
        self.generate_packets()
        if self.queue:
            return [self.queue.pop()]
        else:
            return None

    def receive(self, packet):
        packet.source = self.id
        if packet.destination == self.id:
            print(f'Node {self.id} received packet {packet.id}')
        else:
            self.queue.append(packet)

    def generate_packets(self):
        if self.generation_rate <= 0:
            return None
        else:
            for _ in range(self.generation_rate):
                if not self.destinations:
                    return None
                else:
                    rand_int = np.random.randint(len(self.destinations))
                    self.queue.append(packet.Packet(self.id, self.destinations[rand_int]))

    def __hash__(self):
        return hash(self.id)