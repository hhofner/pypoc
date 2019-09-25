import packet
import numpy as np
import generation_models
from collections import deque

verbose = False
verboseprint = print if verbose else lambda *a, **k: None

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
        self.queue = deque()
        self.time  = 0
        self.dropped_packets = [] #TODO: Better implementation pls
        self.topology = None

        self.config = {'generation_rate': 0,
                       'destinations': [],
                       'type': 'node',
                       'serv_rate': 0,
                       'queue_cap': 0,
                       'gen_scheme': '',
                       'logging_file': '',
                       'transmission_rate': 0,}

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
        '''
        Receive packet object and either add to its queue, or drop the packet
        if the queue is full.

        :param packet: Packet
        :return: None
        '''
        try:
            self.queue_cap_current
        except AttributeError:
            self.queue_cap_current = self.config['queue_cap']

        if packet.destination == self.id:
            print(f'Node {self.id} received packet {packet.id}')
        else:
            if not packet.size < self.queue_cap_current:
                packet.set_current_node(self.id)
                self.queue_cap_current -= packet.size
                self.queue.append(packet)
            else:
                self.dropped_packets.append(packet)

    def generate_packets(self):
        '''
        Set and call \'gen_func\', which generates packages and adds Packet instances
        to the Node objects queue.

        Supported types of generation schemes:
        1. \'linear\' : default gen scheme which generates \'generation_rate\' number of packets every time step
        2. \'basic_normal\' : generate packets based on a normal distribution around \'generation_rate\',
                              if node object contains \'standard_dev\' configuration, use that configuration for
                              the standard deviation, else a default value is used.
        3. \'time_experimental\' : experimental generation scheme with no set functionality. Used for testing purposes.
        :return: None
        '''
        if self.config['gen_scheme'] == 'linear':
            gen_func = generation_models.basic_linear_generation
        elif self.config['gen_scheme'] == 'basic_normal':
            gen_func = generation_models.basic_normal_generation
        elif self.config['gen_scheme'] == 'time_experimental':
            gen_func = generation_models.time_experimental_generation
        else:
            gen_func = None
            verboseprint(f'Generation model is not set for node {self.id}') #TODO: Log this

        if gen_func:
            gen_func(self)

    def service(self):
        '''
        Method that returns a list of packets from queue to be transmitted. Traverse through queue appending
        to list of packets to be transmitted. Stop whenever queue is empty or when serv_rate is reached, whichever
        comes first.

        :return: List(Packet) or None
        '''
        packets_to_send = []
        serv_rate = self.config['serv_rate']
        if serv_rate <= 0:
            verboseprint(f'Warning: Serve rate is set to 0 for Node {self.id}')
        if self.queue:
            for _ in range(len(self.queue)):
                if serv_rate > 0:
                    try:
                        to_be_sent = self.queue.popleft()
                    except IndexError:
                        if packets_to_send:
                            return packets_to_send
                        else:
                            return None
                    else:
                        packets_to_send.append(to_be_sent)
                        serv_rate -= to_be_sent.size
                        try:
                            self.queue_cap_current += to_be_sent.size
                        except AttributeError:
                            pass
                else:
                    return packets_to_send

            return packets_to_send
        else:
            return None

    def __hash__(self):
        return hash(self.id)