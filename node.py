class Node:
    def __init__(self):
        self.id

        self.x
        self.y
        self.z

        self.linkNum
        self.packageCount
        self.GWNum
        self.GWHop
        self.random
        self.sigCount
        self.pacNum
        self.speed
        self.outputCount

        self.allDelay = 0.0
        self.allOneHopDelay = 0.0

        self.nodeTime
        self.packageRate
        self.perTransDelay
        self.perTransSignalDelay
        self.energy

        self.transRange = 70.0
        self.shortestDistance = None # Is initially represented as 9999999 to represent infinity

    def __str__(self):
        s =  "Node " + self.id + "\n￿￿"
        s += "x: " + str(self.x) + ", y: " + str(self.y)