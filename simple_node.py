import packet
import numpy as np
import generation_models

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
        self.time  = 0
        self.dropped_packets = [] #TODO: Better implementation pls

        self.config = {'generation_rate': 0,
                       'destinations': [],
                       'type': 'node',
                       'serv_rate': 10,
                       'queue_cap': 350,
                       'gen_scheme': 'linear',}

        self.update(**kwargs)

    def update(self, **kwargs):
        for key in kwargs.keys():
            if key in self.config.keys():
                if isinstance(kwargs[key], type(self.config[key])):
                    self.config[key] = kwargs[key]
                else:
                    #TODO: Logging
                    raise Exception(f'kwargs[{key}] is not of type {self.config[key]}')

    def transmit(self):
        self.generate_packets()
        return self.service()

    def receive(self, packet):
        try:
            queue_cap = self.config['queue_cap']
        except KeyError as err:
            raise err

        packet.source = self.id
        if packet.destination == self.id:
            print(f'Node {self.id} received packet {packet.id}')
        else:
            if not len(self.queue) >= queue_cap:
                self.queue.append(packet)
            else:
                self.dropped_packets.append(packet)

    def generate_packets(self):
        generation_rate = self.config['generation_rate']
        destinations = self.config['destinations']
        if generation_rate <= 0:
            return None
        else:
            for _ in range(generation_rate):
                if not destinations:
                    return None
                else:
                    rand_int = np.random.randint(len(destinations))
                    self.queue.append(packet.Packet(self.id, destinations[rand_int]))

    def service(self):
        packets_to_send = []
        serv_rate = self.config['serv_rate']
        if self.queue:
            for _ in range(serv_rate):
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

class VaryingPacketGeneratingNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, **kwargs):
        super().update(**kwargs)

    def generate_packets(self):
        if self.config['gen_scheme'] == 'linear':
            gen_func = generation_models.basic_linear_generation
        elif self.config['gen_scheme'] == 'basic_normal':
            gen_func = generation_models.basic_normal_generation
        elif self.config['gen_scheme'] == 'time_experimental':
            gen_func = generation_models.time_experimental_generation

        gen_func(self)