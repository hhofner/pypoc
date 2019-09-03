class Package:
    def __init__(self):
        self.id
        self.size

        self._delay
        self.generateTime
        self.terminalTime

        self.source
        self.destination
        self.hop
        self.path
        self.signaling

    @property
    def delay(self):
        self._delay = self.terminalTime - self.generateTime
        return self._delay

