class Channel(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.packets_carried = []