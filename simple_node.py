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
                       'destinations': [],
                       'type': 'node',
                       'serv_rate': 1}
        self.update(**kwargs)

    def update(self, **kwargs):
        for key in kwargs.keys():
            if key in self.config.keys():
                if isinstance(kwargs[key], type(self.config[key])):
                    self.config[key] = kwargs[key]
                else:
                    #TODO: Logging
                    pass

        self.generation_rate = self.config['generation_rate']
        self.destinations = self.config['destinations']
        self.type = self.config['type']
        self.serv_rate = self.config['serv_rate']

    def transmit(self):
        self.generate_packets()
        return self.service()

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

    def service(self):
        packets_to_send = []
        if self.queue:
            for _ in range(self.serv_rate):
                try:
                    packets_to_send.append(self.queue.pop())
                except IndexError:
                    #TODO: Logging
                    break
            return packets_to_send
        else:
            return None

    def __hash__(self):
        return hash(self.id)