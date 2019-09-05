class Packet:
    current_id = 0
    @staticmethod
    def get_id():
        id = Packet.current_id
        Packet.current_id += 1
        return id

    def __init__(self, **kwargs):
        self.id = Packet.get_id()
        self.size = kwargs['size']

        self.source = kwargs['source']
        self.destination = kwargs['destination']
        self.path = kwargs['path']
        self.hops = 0

        # self.generate_time = kwargs['generate_time'] if 'generate_time' in kwargs.keys() else 0
        # self.terminal_time = kwargs['terminal_time'] if 'terminal_time' in kwargs.keys() else 0
        # self._delay = 0
        #
        # self.signaling = False

    def next_hop(self):
        if self.path:
            self.hops += 1
            return self.path.pop()
