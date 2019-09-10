class Packet:
    current_id = 0
    @staticmethod
    def get_id():
        id = Packet.current_id
        Packet.current_id += 1
        return id

    def __init__(self, source, destination):
        self.id = Packet.get_id()

        self.source         = source
        self.destination    = destination
        self._initial_source = source

        self.path = []

    def next_hop(self):
        if not self.path[0] == self.source:
            raise Exception(f'Path problems, first node on path and source IDs do not match!'
                            f'{self.source} =/= {self.path[0]}')

    def __repr__(self):
        s = f'Packet({self.id}, init_source:{self._initial_source}, current_source: {self.source}, dest:{self.destination}'
        s += f' path:{self.path})'

        return s
