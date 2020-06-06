class Packet:
    arrived_count = 0
    dropped_count = 0
    generated_count = 0

    @staticmethod
    def reset():
        Packet.arrived_count = 0
        Packet.dropped_count = 0
        Packet.generated_count = 0


    def __init__(self, path, tick_time, size=1):
        '''
        Increments the Packet class-wide generated_count variable and
        assigns object attributes.

        :param path: List of Node objects representing a path from src to dest.
        :param size: Integer representing an arbitrary size of the Packet.
        '''
        self.size: int = size

        self._has_arrived = False
        self._has_dropped = False
        self.id = Packet.generated_count
        Packet.generated_count += 1

        self.path_nodes = {'past': [], 'future': []}
        self.path_nodes['past'].append(path[0])
        self.path_nodes['future'].extend(path[1:])

        # The `tick` at which the packet object was instanitated
        self.born_tick = tick_time
        self.died_tick = None

    def check_and_update_path(self, arrived_node, tick):
        '''
        Check if the Node that received `this` packet aligns with
        the path, and if so, update. If path empty, it means it
        arrived at destination node.

        :param arrived_node: Node object
        '''
        if arrived_node is self.path_nodes['future'][0]:
            arrived_node = self.path_nodes['future'][0]
            self.path_nodes['past'].append(arrived_node)
            self.path_nodes['future'].remove(arrived_node)
        else:
            raise Exception(f'Next node in path does not match! '
                            f'{arrived_node} =/= '
                            f'{self.path_nodes["future"][0]}')

        # If empty no more future
        if not self.path_nodes['future']:
            self.arrived(tick)

    def arrived(self, tick):
        if not self._has_arrived:
            Packet.arrived_count += 1
            # print(f'{self} arrived!')
            self.died_tick = tick
            self.delay = self.died_tick - self.born_tick
        self._has_arrived = True
        # Update average delay

    def dropped(self):
        if not self._has_dropped:
            Packet.dropped_count += 1
        self._has_dropped = True

    @property
    def next_node(self):
        return self.path_nodes['future'][0]

    def __str__(self):
        return f'packet_{self.id}'

    def __repr__(self):
        return f'Packet(ID:{self.id}, SIZE:{self.size})'


