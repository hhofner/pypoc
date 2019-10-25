class Channel:
    def __init__(self, bandwidth):
        self.bandwidth = bandwidth
        self.data_in_chan = []
        self.accessing_nodes = []

    def in(self, data):
        if data is list:
            self.data_in_chan.extend(data)
        else:
            self.data_in_chan.append(data)

    def out(self):
        for p in self.data_in_chan:
            try:
                id = p.next_node_id
